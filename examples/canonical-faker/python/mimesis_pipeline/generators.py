from __future__ import annotations

# Mimesis generates realistic atomic values. This module adds the relational graph layer on top.

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from mimesis import Address, Datetime, Finance, Generic, Internet, Person, Text
    from mimesis.locales import Locale
    from mimesis.providers import BaseProvider
    from mimesis.schema import Field, Schema
except ImportError:  # pragma: no cover - exercised by importability tests
    Address = Datetime = Finance = Generic = Internet = Person = Text = None
    Locale = None
    BaseProvider = object
    Field = Schema = None


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


class TenantCoreProvider(BaseProvider):
    class Meta:
        name = "tenantcore"

    def __init__(self, seed: int):
        super().__init__()
        self._rng = domain.random.Random(seed)

    def plan(self) -> str:
        return domain._weighted_choice(self._rng, domain.PLAN_CHOICES)

    def region(self) -> str:
        return domain._weighted_choice(self._rng, domain.REGION_CHOICES)

    def role(self) -> str:
        return domain._weighted_choice(self._rng, domain.ROLE_CHOICES)


def _require_mimesis() -> None:
    if Generic is None or Field is None or Schema is None:
        raise RuntimeError("mimesis is required for the Mimesis pipeline")


def _schema_orgs(profile: Profile, provider: TenantCoreProvider, rng) -> list[dict]:
    field = Field(locale=Locale.EN, seed=profile.seed)
    schema = Schema(
        schema=lambda: {
            "seed_id": field("uuid"),
            "name": field("company"),
            "owner_email": field("email"),
        }
    )
    rows = schema.create(iterations=profile.num_orgs)
    orgs: list[dict] = []
    seen_slugs: set[str] = set()
    for index, row in enumerate(rows):
        base_slug = domain._slugify(row["name"])
        slug = base_slug
        suffix = 1
        while slug in seen_slugs:
            suffix += 1
            slug = f"{base_slug}-{suffix}"
        seen_slugs.add(slug)
        orgs.append(
            {
                "id": row.get("seed_id") or domain._deterministic_uuid(rng),
                "name": row["name"],
                "slug": slug,
                "plan": provider.plan(),
                "region": provider.region(),
                "created_at": domain._iso(domain._past_timestamp(rng)),
                "owner_email": row["owner_email"].lower(),
                "sequence": index,
            }
        )
    return orgs


def _user_generators(profile: Profile):
    seeds = {
        "en-US": profile.seed + 11,
        "en-GB": profile.seed + 12,
        "de-DE": profile.seed + 13,
        "fr-FR": profile.seed + 14,
    }
    return {
        "en-US": Generic(locale=Locale.EN, seed=seeds["en-US"]),
        "en-GB": Generic(locale=Locale.EN_GB, seed=seeds["en-GB"]),
        "de-DE": Generic(locale=Locale.DE, seed=seeds["de-DE"]),
        "fr-FR": Generic(locale=Locale.FR, seed=seeds["fr-FR"]),
    }


def _build_users(profile: Profile, rng) -> list[dict]:
    users: list[dict] = []
    seen_emails: set[str] = set()
    generators = _user_generators(profile)
    for index in range(profile.num_users):
        locale_code = domain._weighted_choice(rng, domain.LOCALE_CHOICES)
        generic = generators[locale_code]
        email = generic.internet.email().lower()
        while email in seen_emails:
            email = f"user{index}-{rng.randint(1000, 9999)}@tenantcore.test"
        seen_emails.add(email)
        name = generic.person.full_name()
        _ = {
            "address": generic.address.address(),
            "text": generic.text.word(),
        }
        users.append(
            {
                "id": domain._deterministic_uuid(rng),
                "email": email,
                "full_name": name,
                "locale": locale_code,
                "timezone": domain.TIMEZONE_BY_LOCALE[locale_code],
                "created_at": domain._iso(domain._past_timestamp(rng)),
                "sequence": index,
            }
        )
    return users


def _build_memberships(orgs: list[dict], users: list[dict], provider: TenantCoreProvider, rng):
    memberships: list[dict] = []
    org_member_map: dict[str, list[str]] = {}
    users_by_id = {user["id"]: user for user in users}
    user_ids = [user["id"] for user in users]
    for org in orgs:
        target_count = domain._bounded_count(rng, 3, min(50, len(users)), 6, cap=len(users))
        member_ids = rng.sample(user_ids, k=target_count)
        org_created = datetime.fromisoformat(org["created_at"].replace("Z", "+00:00"))
        org_member_map[org["id"]] = list(member_ids)
        for position, user_id in enumerate(member_ids):
            role = "owner" if position == 0 else provider.role()
            joined_at = org_created + timedelta(
                days=rng.randint(0, 365), seconds=rng.randint(0, 7200)
            )
            inviter_candidates = member_ids[:position]
            invited_by = rng.choice(inviter_candidates) if inviter_candidates else None
            memberships.append(
                {
                    "id": domain._deterministic_uuid(rng),
                    "org_id": org["id"],
                    "user_id": user_id,
                    "role": role,
                    "joined_at": domain._iso(joined_at),
                    "invited_by": invited_by,
                    "user_email": users_by_id[user_id]["email"],
                }
            )
    return memberships, org_member_map


def _build_projects(orgs: list[dict], org_member_map: dict[str, list[str]], profile: Profile, rng):
    projects: list[dict] = []
    project_org_map: dict[str, str] = {}
    generic = Generic(locale=Locale.EN, seed=profile.seed + 21)
    for org in orgs:
        org_created = datetime.fromisoformat(org["created_at"].replace("Z", "+00:00"))
        count = domain._bounded_count(rng, 1, 20, 3.5)
        for _ in range(count):
            project_id = domain._deterministic_uuid(rng)
            created_by = rng.choice(org_member_map[org["id"]])
            projects.append(
                {
                    "id": project_id,
                    "org_id": org["id"],
                    "name": f"{generic.text.word().title()} {generic.text.word().title()}",
                    "status": domain._weighted_choice(rng, domain.PROJECT_STATUS_CHOICES),
                    "created_by": created_by,
                    "created_at": domain._iso(
                        org_created
                        + timedelta(days=rng.randint(0, 540), seconds=rng.randint(0, 7200))
                    ),
                }
            )
            project_org_map[project_id] = org["id"]
    return projects, project_org_map


def _build_api_keys(orgs: list[dict], org_member_map: dict[str, list[str]], profile: Profile, rng):
    api_keys: list[dict] = []
    seen_prefixes: set[str] = set()
    finance = Finance(seed=profile.seed + 31)
    text = Text(locale=Locale.EN, seed=profile.seed + 32)
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    for org in orgs:
        org_created = datetime.fromisoformat(org["created_at"].replace("Z", "+00:00"))
        count = domain._bounded_count(rng, 0, 10, 2)
        for _ in range(count):
            suffix = "".join(rng.choice(alphabet) for _ in range(8))
            key_prefix = f"tc_{suffix}"
            while key_prefix in seen_prefixes:
                suffix = "".join(rng.choice(alphabet) for _ in range(8))
                key_prefix = f"tc_{suffix}"
            seen_prefixes.add(key_prefix)
            created_at = org_created + timedelta(
                days=rng.randint(0, 540), seconds=rng.randint(0, 3600)
            )
            last_used_at = None
            if rng.random() > 0.30:
                last_used_at = domain._iso(
                    created_at
                    + timedelta(days=rng.randint(0, 180), seconds=rng.randint(0, 3600))
                )
            api_keys.append(
                {
                    "id": domain._deterministic_uuid(rng),
                    "org_id": org["id"],
                    "created_by": rng.choice(org_member_map[org["id"]]),
                    "name": f"{text.word().title()} access {finance.currency_iso_code()}",
                    "key_prefix": key_prefix,
                    "created_at": domain._iso(created_at),
                    "last_used_at": last_used_at,
                }
            )
    return api_keys


def _build_invitations(
    orgs: list[dict], org_member_map: dict[str, list[str]], users: list[dict], profile: Profile, rng
):
    invitations: list[dict] = []
    internet = Internet(seed=profile.seed + 41)
    users_by_id = {user["id"]: user for user in users}
    for org in orgs:
        member_emails = {
            users_by_id[user_id]["email"].lower() for user_id in org_member_map[org["id"]]
        }
        count = domain._bounded_count(rng, 0, 5, 1.5)
        for _ in range(count):
            invited_email = internet.email().lower()
            while invited_email in member_emails:
                invited_email = internet.email().lower()
            accepted_at = None
            if rng.random() < 0.40:
                accepted_at = domain._iso(domain._past_timestamp(rng, days_back=180))
            invitations.append(
                {
                    "id": domain._deterministic_uuid(rng),
                    "org_id": org["id"],
                    "invited_email": invited_email,
                    "role": domain._weighted_choice(rng, domain.INVITATION_ROLE_CHOICES),
                    "invited_by": rng.choice(org_member_map[org["id"]]),
                    "expires_at": domain._iso(domain._future_timestamp(rng)),
                    "accepted_at": accepted_at,
                }
            )
    return invitations


def _build_audit_events(
    orgs: list[dict],
    org_member_map: dict[str, list[str]],
    memberships: list[dict],
    projects: list[dict],
    project_org_map: dict[str, str],
    api_keys: list[dict],
    invitations: list[dict],
    profile: Profile,
    rng,
):
    audit_events: list[dict] = []
    memberships_by_org: dict[str, list[dict]] = {}
    membership_lookup: dict[tuple[str, str], dict] = {}
    api_keys_by_org: dict[str, list[dict]] = {}
    invitations_by_org: dict[str, list[dict]] = {}
    generic = Generic(locale=Locale.EN, seed=profile.seed + 51)
    dt_provider = Datetime(seed=profile.seed + 52)
    for membership in memberships:
        memberships_by_org.setdefault(membership["org_id"], []).append(membership)
        membership_lookup[(membership["org_id"], membership["user_id"])] = membership
    for api_key in api_keys:
        api_keys_by_org.setdefault(api_key["org_id"], []).append(api_key)
    for invitation in invitations:
        invitations_by_org.setdefault(invitation["org_id"], []).append(invitation)
    for project in projects:
        org_id = project_org_map[project["id"]]
        project_created = datetime.fromisoformat(project["created_at"].replace("Z", "+00:00"))
        if project["status"] == "active":
            count = domain._bounded_count(rng, 8, 30, 14)
        elif project["status"] == "archived":
            count = domain._bounded_count(rng, 4, 18, 8)
        else:
            count = domain._bounded_count(rng, 2, 10, 4)
        for _ in range(count):
            user_id = rng.choice(org_member_map[org_id])
            membership = membership_lookup[(org_id, user_id)]
            joined_at = datetime.fromisoformat(membership["joined_at"].replace("Z", "+00:00"))
            event_floor = max(project_created, joined_at)
            resource_candidates = [
                ("project", project["id"]),
                ("user", user_id),
                *[("membership", row["id"]) for row in memberships_by_org.get(org_id, [])],
                *[("api_key", row["id"]) for row in api_keys_by_org.get(org_id, [])],
                *[("invitation", row["id"]) for row in invitations_by_org.get(org_id, [])],
            ]
            resource_type, resource_id = rng.choice(resource_candidates)
            ts = event_floor + timedelta(days=rng.randint(0, 365), seconds=rng.randint(0, 3600))
            _ = {
                "event_time": dt_provider.datetime(start=event_floor, end=domain.BASE_TIME),
                "label": generic.text.word(),
            }
            audit_events.append(
                {
                    "id": domain._deterministic_uuid(rng),
                    "org_id": org_id,
                    "user_id": user_id,
                    "project_id": project["id"],
                    "action": domain._weighted_choice(rng, domain.AUDIT_ACTION_CHOICES),
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "ts": domain._iso(min(ts, domain.BASE_TIME)),
                }
            )
    audit_events.sort(key=lambda row: row["ts"])
    return audit_events


def run_mimesis_pipeline(
    profile: Profile, output_dir: Path, formats: tuple[str, ...] = ("jsonl",)
) -> ValidationReport:
    _require_mimesis()
    rng = domain.random.Random(profile.seed)
    provider = TenantCoreProvider(profile.seed)

    organizations = _schema_orgs(profile, provider, rng)
    users = _build_users(profile, rng)
    memberships, org_member_map = _build_memberships(organizations, users, provider, rng)
    projects, project_org_map = _build_projects(organizations, org_member_map, profile, rng)
    api_keys = _build_api_keys(organizations, org_member_map, profile, rng)
    invitations = _build_invitations(organizations, org_member_map, users, profile, rng)
    audit_events = _build_audit_events(
        organizations,
        org_member_map,
        memberships,
        projects,
        project_org_map,
        api_keys,
        invitations,
        profile,
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
    report = domain.validate_dataset(dataset)
    dataset["report"] = report
    if not report.ok:
        raise ValueError("Mimesis pipeline generated an invalid dataset")
    if "jsonl" in formats:
        domain.write_jsonl(dataset, output_dir, profile.name)
    if "csv" in formats:
        domain.write_csv(dataset, output_dir, profile.name)
    return report
