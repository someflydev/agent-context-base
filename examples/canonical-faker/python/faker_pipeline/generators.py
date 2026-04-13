from __future__ import annotations

"""Faker pipeline for TenantCore.

Edge-case injection rates:
- 5% of generated users receive a deliberate edge-case profile.
- Edge-case users use a near-254-character email, a non-ASCII display name,
  and timezone `UTC` to exercise downstream boundary handling.
"""

import importlib.util
import json
import sys
from collections import OrderedDict
from pathlib import Path

try:
    from faker import Faker
    from faker.providers import BaseProvider
except ImportError:  # pragma: no cover - exercised by importability tests
    BaseProvider = object
    Faker = None


MIXED_LOCALES = [
    ("en-US", "en_US", 0.60),
    ("en-GB", "en_GB", 0.20),
    ("de-DE", "de_DE", 0.10),
    ("fr-FR", "fr_FR", 0.10),
]
EDGE_CASE_NAMES = [
    "Sofie D'Aubigne",
    "Bjorn Asmussen",
    "Francois L'Ecuyer",
    "Marta Nunez de la Pena",
    "Zoe Kruger-Renaud",
]


def _load_domain_module():
    module_path = Path(__file__).resolve().parents[2] / "domain" / "generation_patterns.py"
    spec = importlib.util.spec_from_file_location(
        "canonical_faker_domain_generation_patterns", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load domain module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


domain = _load_domain_module()
Profile = domain.Profile
ValidationReport = domain.ValidationReport


class CustomProvider(BaseProvider):
    def tenant_core_plan(self) -> str:
        return self.random_element(
            elements=OrderedDict([("free", 0.50), ("pro", 0.35), ("enterprise", 0.15)])
        )

    def tenant_core_region(self) -> str:
        return self.random_element(
            elements=OrderedDict(
                [
                    ("us-east", 0.40),
                    ("us-west", 0.25),
                    ("eu-west", 0.20),
                    ("ap-southeast", 0.15),
                ]
            )
        )


def _require_faker() -> None:
    if Faker is None:
        raise RuntimeError("faker is required for the Faker pipeline")


def _locale_fakers(seed: int):
    weighted = Faker([item[1] for item in MIXED_LOCALES], use_weighting=True)
    weighted.seed_instance(seed)
    weighted.add_provider(CustomProvider)
    by_locale = {}
    for offset, (_, faker_locale, _) in enumerate(MIXED_LOCALES):
        fake = Faker(faker_locale)
        fake.seed_instance(seed + offset + 1)
        by_locale[faker_locale] = fake
    return weighted, by_locale


def _long_email(index: int, locale_code: str) -> str:
    suffix = f".{locale_code.lower().replace('-', '')}.{index}@tenantcore-example.test"
    local_len = 254 - len(suffix)
    local = ("edgecase" + str(index))[:local_len].ljust(local_len, "x")
    return f"{local}{suffix}"


def _build_organizations(profile: Profile, rng, fake) -> list[dict]:
    orgs: list[dict] = []
    seen_slugs: set[str] = set()
    seen_emails: set[str] = set()
    for index in range(profile.num_orgs):
        name = fake.unique.company()
        base_slug = domain._slugify(name)
        slug = base_slug
        suffix = 1
        while slug in seen_slugs:
            suffix += 1
            slug = f"{base_slug}-{suffix}"
        seen_slugs.add(slug)
        email = fake.unique.company_email()
        while email in seen_emails:
            email = fake.unique.company_email()
        seen_emails.add(email)
        orgs.append(
            {
                "id": domain._deterministic_uuid(rng),
                "name": name,
                "slug": slug,
                "plan": fake.tenant_core_plan(),
                "region": fake.tenant_core_region(),
                "created_at": domain._iso(domain._past_timestamp(rng)),
                "owner_email": email,
                "sequence": index,
            }
        )
    return orgs


def _build_users(profile: Profile, rng, fake, locale_map) -> list[dict]:
    users: list[dict] = []
    seen_emails: set[str] = set()
    locale_pairs = [(label, weight) for label, _, weight in MIXED_LOCALES]
    faker_by_label = {label: locale_map[faker_locale] for label, faker_locale, _ in MIXED_LOCALES}
    for index in range(profile.num_users):
        locale_code = domain._weighted_choice(rng, locale_pairs)
        locale_fake = faker_by_label[locale_code]
        edge_case = rng.random() < 0.05
        email = locale_fake.unique.email().lower()
        if edge_case:
            email = _long_email(index, locale_code)
        while email in seen_emails:
            email = locale_fake.unique.email().lower()
        seen_emails.add(email)
        full_name = locale_fake.name()
        timezone = domain.TIMEZONE_BY_LOCALE[locale_code]
        if edge_case:
            full_name = EDGE_CASE_NAMES[index % len(EDGE_CASE_NAMES)]
            timezone = "UTC"
        # Generated for locale consistency demonstration; not persisted to output.
        _ = {
            "street": locale_fake.street_address(),
            "phone": locale_fake.phone_number(),
        }
        users.append(
            {
                "id": domain._deterministic_uuid(rng),
                "email": email,
                "full_name": full_name,
                "locale": locale_code,
                "timezone": timezone,
                "created_at": domain._iso(domain._past_timestamp(rng)),
                "sequence": index,
            }
        )
    return users


def _finalize_dataset(profile: Profile, dataset: dict, output_dir: Path, formats: tuple[str, ...]):
    report = domain.validate_dataset(dataset)
    dataset["report"] = report
    if not report.ok:
        raise ValueError("Faker pipeline generated an invalid dataset")
    if "jsonl" in formats:
        domain.write_jsonl(dataset, output_dir, profile.name)
    if "csv" in formats:
        domain.write_csv(dataset, output_dir, profile.name)
    return report


def run_faker_pipeline(
    profile: Profile, output_dir: Path, formats: tuple[str, ...] = ("jsonl",)
) -> ValidationReport:
    _require_faker()
    weighted_fake, locale_map = _locale_fakers(profile.seed)
    domain.Faker.seed(profile.seed)
    domain._ACTIVE_FAKER = weighted_fake
    rng = domain.random.Random(profile.seed)

    organizations = _build_organizations(profile, rng, weighted_fake)
    users = _build_users(profile, rng, weighted_fake, locale_map)
    memberships, org_member_map = domain.build_membership_pool(organizations, users, rng)
    projects, project_org_map = domain.build_project_pool(organizations, org_member_map, rng)
    api_keys = domain.build_api_key_pool(organizations, org_member_map, rng)
    invitations = domain.build_invitation_pool(organizations, org_member_map, users, rng)
    audit_events = domain.build_audit_event_pool(
        organizations,
        org_member_map,
        memberships,
        projects,
        project_org_map,
        api_keys,
        invitations,
        rng,
    )

    dataset = {
        "profile": profile.name,
        "seed": profile.seed,
        "organizations": organizations,
        "users": users,
        "memberships": memberships,
        "projects": projects,
        "audit_events": audit_events,
        "api_keys": api_keys,
        "invitations": invitations,
    }
    return _finalize_dataset(profile, dataset, output_dir, formats)


def validation_summary(report: ValidationReport) -> str:
    payload = {
        "ok": report.ok,
        "profile": report.profile,
        "seed": report.seed,
        "counts": report.counts,
        "violations": report.violations,
    }
    return json.dumps(payload, indent=2, sort_keys=True)
