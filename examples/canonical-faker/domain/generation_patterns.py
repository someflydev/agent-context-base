from __future__ import annotations

import csv
import json
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

try:
    from faker import Faker
except ImportError:  # pragma: no cover - exercised by importability tests
    Faker = None


_ACTIVE_FAKER = None

PLAN_CHOICES = [("free", 0.50), ("pro", 0.35), ("enterprise", 0.15)]
REGION_CHOICES = [
    ("us-east", 0.40),
    ("us-west", 0.25),
    ("eu-west", 0.20),
    ("ap-southeast", 0.15),
]
LOCALE_CHOICES = [
    ("en-US", 0.60),
    ("en-GB", 0.20),
    ("de-DE", 0.10),
    ("fr-FR", 0.10),
]
TIMEZONE_BY_LOCALE = {
    "en-US": "America/New_York",
    "en-GB": "Europe/London",
    "de-DE": "Europe/Berlin",
    "fr-FR": "Europe/Paris",
}
ROLE_CHOICES = [("owner", 0.05), ("admin", 0.10), ("member", 0.60), ("viewer", 0.25)]
PROJECT_STATUS_CHOICES = [("active", 0.60), ("archived", 0.25), ("draft", 0.15)]
AUDIT_ACTION_CHOICES = [
    ("updated", 0.35),
    ("created", 0.20),
    ("exported", 0.15),
    ("invited", 0.12),
    ("archived", 0.10),
    ("deleted", 0.08),
]
RESOURCE_TYPE_CHOICES = [
    ("project", 0.35),
    ("user", 0.15),
    ("membership", 0.25),
    ("api_key", 0.10),
    ("invitation", 0.15),
]
INVITATION_ROLE_CHOICES = [("admin", 0.15), ("member", 0.65), ("viewer", 0.20)]
BASE_TIME = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
ENTITY_ORDER = [
    "organizations",
    "users",
    "memberships",
    "projects",
    "audit_events",
    "api_keys",
    "invitations",
]


@dataclass(frozen=True)
class Profile:
    name: str
    num_orgs: int
    num_users: int
    seed: int

    @classmethod
    def SMOKE(cls) -> "Profile":
        return cls(name="smoke", num_orgs=3, num_users=10, seed=42)

    @classmethod
    def SMALL(cls) -> "Profile":
        return cls(name="small", num_orgs=20, num_users=200, seed=1000)

    @classmethod
    def MEDIUM(cls) -> "Profile":
        return cls(name="medium", num_orgs=200, num_users=5000, seed=5000)

    @classmethod
    def LARGE(cls) -> "Profile":
        return cls(name="large", num_orgs=2000, num_users=50000, seed=9999)


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    violations: list[str]
    counts: dict[str, int]
    seed: int
    profile: str


def _require_faker() -> None:
    if Faker is None:
        raise RuntimeError("faker is required to generate datasets")


def _fake():
    if _ACTIVE_FAKER is None:
        raise RuntimeError("faker runtime is not initialized")
    return _ACTIVE_FAKER


def _weighted_choice(rng: random.Random, pairs: list[tuple[str, float]]) -> str:
    values = [value for value, _ in pairs]
    weights = [weight for _, weight in pairs]
    return rng.choices(values, weights=weights, k=1)[0]


def _deterministic_uuid(rng: random.Random) -> str:
    raw = rng.getrandbits(128)
    return str(uuid.UUID(int=raw, version=4))


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _slugify(value: str) -> str:
    slug = []
    last_dash = False
    for char in value.lower():
        if char.isalnum():
            slug.append(char)
            last_dash = False
        elif not last_dash:
            slug.append("-")
            last_dash = True
    return "".join(slug).strip("-") or "tenantcore"


def _past_timestamp(rng: random.Random, *, days_back: int = 365 * 3) -> datetime:
    days = rng.randint(1, days_back)
    seconds = rng.randint(0, 24 * 60 * 60 - 1)
    return BASE_TIME - timedelta(days=days, seconds=seconds)


def _future_timestamp(rng: random.Random, *, days_forward: int = 30) -> datetime:
    days = rng.randint(1, days_forward)
    seconds = rng.randint(0, 24 * 60 * 60 - 1)
    return BASE_TIME + timedelta(days=days, seconds=seconds)


def _bounded_count(
    rng: random.Random,
    minimum: int,
    maximum: int,
    mode: float,
    cap: int | None = None,
) -> int:
    count = int(round(rng.triangular(minimum, maximum, mode)))
    if cap is not None:
        count = min(count, cap)
    return max(minimum, min(maximum, count))


def _chunked(rows: list[dict], chunk_size: int) -> Iterable[list[dict]]:
    for index in range(0, len(rows), chunk_size):
        yield rows[index : index + chunk_size]


def _minimum_row_count(entity: str) -> int:
    if entity in {"api_keys", "invitations"}:
        return 0
    return 1


def build_org_pool(profile: Profile, rng: random.Random) -> list[dict]:
    _require_faker()
    fake = _fake()
    orgs: list[dict] = []
    seen_slugs: set[str] = set()
    seen_emails: set[str] = set()
    for index in range(profile.num_orgs):
        name = fake.unique.company()
        base_slug = _slugify(name)
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
                "id": _deterministic_uuid(rng),
                "name": name,
                "slug": slug,
                "plan": _weighted_choice(rng, PLAN_CHOICES),
                "region": _weighted_choice(rng, REGION_CHOICES),
                "created_at": _iso(_past_timestamp(rng)),
                "owner_email": email,
                "sequence": index,
            }
        )
    return orgs


def build_user_pool(profile: Profile, rng: random.Random) -> list[dict]:
    _require_faker()
    fake = _fake()
    users: list[dict] = []
    seen_emails: set[str] = set()
    for index in range(profile.num_users):
        locale = _weighted_choice(rng, LOCALE_CHOICES)
        email = fake.unique.email()
        while email in seen_emails:
            email = fake.unique.email()
        seen_emails.add(email)
        users.append(
            {
                "id": _deterministic_uuid(rng),
                "email": email,
                "full_name": fake.name(),
                "locale": locale,
                "timezone": TIMEZONE_BY_LOCALE[locale],
                "created_at": _iso(_past_timestamp(rng)),
                "sequence": index,
            }
        )
    return users


def build_membership_pool(orgs: list[dict], users: list[dict], rng: random.Random) -> tuple[list[dict], dict[str, list[str]]]:
    memberships: list[dict] = []
    org_member_map: dict[str, list[str]] = {}
    users_by_id = {user["id"]: user for user in users}
    user_ids = [user["id"] for user in users]
    for org in orgs:
        target_count = _bounded_count(rng, 3, min(50, len(users)), 6, cap=len(users))
        member_ids = rng.sample(user_ids, k=target_count)
        owner_id = member_ids[0]
        org_member_map[org["id"]] = list(member_ids)
        org_created = datetime.fromisoformat(org["created_at"].replace("Z", "+00:00"))
        for position, user_id in enumerate(member_ids):
            role = "owner" if position == 0 else _weighted_choice(rng, ROLE_CHOICES)
            joined_at = org_created + timedelta(
                days=rng.randint(0, 365), seconds=rng.randint(0, 7200)
            )
            inviter_candidates = member_ids[:position]
            invited_by = None
            if role != "owner" and inviter_candidates:
                invited_by = rng.choice(inviter_candidates)
            memberships.append(
                {
                    "id": _deterministic_uuid(rng),
                    "org_id": org["id"],
                    "user_id": user_id,
                    "role": role,
                    "joined_at": _iso(joined_at),
                    "invited_by": invited_by,
                    "user_email": users_by_id[user_id]["email"],
                }
            )
    return memberships, org_member_map


def build_project_pool(
    orgs: list[dict], org_member_map: dict[str, list[str]], rng: random.Random
) -> tuple[list[dict], dict[str, str]]:
    _require_faker()
    fake = _fake()
    projects: list[dict] = []
    project_org_map: dict[str, str] = {}
    for org in orgs:
        org_created = datetime.fromisoformat(org["created_at"].replace("Z", "+00:00"))
        count = _bounded_count(rng, 1, 20, 3.5)
        for _ in range(count):
            project_id = _deterministic_uuid(rng)
            created_by = rng.choice(org_member_map[org["id"]])
            status = _weighted_choice(rng, PROJECT_STATUS_CHOICES)
            projects.append(
                {
                    "id": project_id,
                    "org_id": org["id"],
                    "name": fake.bs().title(),
                    "status": status,
                    "created_by": created_by,
                    "created_at": _iso(
                        org_created
                        + timedelta(days=rng.randint(0, 540), seconds=rng.randint(0, 7200))
                    ),
                }
            )
            project_org_map[project_id] = org["id"]
    return projects, project_org_map


def build_audit_event_pool(
    orgs: list[dict],
    org_member_map: dict[str, list[str]],
    memberships: list[dict],
    projects: list[dict],
    project_org_map: dict[str, str],
    api_keys: list[dict],
    invitations: list[dict],
    rng: random.Random,
) -> list[dict]:
    audit_events: list[dict] = []
    org_index = {org["id"]: org for org in orgs}
    memberships_by_org: dict[str, list[dict]] = {}
    membership_lookup: dict[tuple[str, str], dict] = {}
    api_keys_by_org: dict[str, list[dict]] = {}
    invitations_by_org: dict[str, list[dict]] = {}
    for membership in memberships:
        memberships_by_org.setdefault(membership["org_id"], []).append(membership)
        membership_lookup[(membership["org_id"], membership["user_id"])] = membership
    for api_key in api_keys:
        api_keys_by_org.setdefault(api_key["org_id"], []).append(api_key)
    for invitation in invitations:
        invitations_by_org.setdefault(invitation["org_id"], []).append(invitation)
    for project in projects:
        org_id = project_org_map[project["id"]]
        member_ids = org_member_map[org_id]
        project_created = datetime.fromisoformat(project["created_at"].replace("Z", "+00:00"))
        if project["status"] == "active":
            count = _bounded_count(rng, 8, 30, 14)
        elif project["status"] == "archived":
            count = _bounded_count(rng, 4, 18, 8)
        else:
            count = _bounded_count(rng, 2, 10, 4)
        for _ in range(count):
            user_id = rng.choice(member_ids)
            membership = membership_lookup[(org_id, user_id)]
            membership_joined_at = datetime.fromisoformat(
                membership["joined_at"].replace("Z", "+00:00")
            )
            event_floor = max(project_created, membership_joined_at)
            resource_candidates: list[tuple[str, str]] = [
                ("project", project["id"]),
                ("user", user_id),
            ]
            resource_candidates.extend(
                ("membership", row["id"]) for row in memberships_by_org.get(org_id, [])
            )
            resource_candidates.extend(
                ("api_key", row["id"]) for row in api_keys_by_org.get(org_id, [])
            )
            resource_candidates.extend(
                ("invitation", row["id"]) for row in invitations_by_org.get(org_id, [])
            )
            resource_type, resource_id = rng.choice(resource_candidates)
            ts = project_created + timedelta(
                days=rng.randint(0, 365), seconds=rng.randint(0, 24 * 60 * 60 - 1)
            )
            if ts < event_floor:
                ts = event_floor + timedelta(seconds=rng.randint(0, 3600))
            audit_events.append(
                {
                    "id": _deterministic_uuid(rng),
                    "org_id": org_id,
                    "user_id": user_id,
                    "project_id": project["id"],
                    "action": _weighted_choice(rng, AUDIT_ACTION_CHOICES),
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "ts": _iso(ts),
                }
            )
    audit_events.sort(key=lambda row: row["ts"])
    return audit_events


def build_api_key_pool(
    orgs: list[dict], org_member_map: dict[str, list[str]], rng: random.Random
) -> list[dict]:
    _require_faker()
    fake = _fake()
    api_keys: list[dict] = []
    seen_prefixes: set[str] = set()
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    for org in orgs:
        org_created = datetime.fromisoformat(org["created_at"].replace("Z", "+00:00"))
        count = _bounded_count(rng, 0, 10, 2)
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
            used_delta = rng.random()
            last_used_at = None
            if used_delta > 0.30:
                last_used_at = _iso(
                    created_at
                    + timedelta(days=rng.randint(0, 180), seconds=rng.randint(0, 3600))
                )
            api_keys.append(
                {
                    "id": _deterministic_uuid(rng),
                    "org_id": org["id"],
                    "created_by": rng.choice(org_member_map[org["id"]]),
                    "name": fake.catch_phrase(),
                    "key_prefix": key_prefix,
                    "created_at": _iso(created_at),
                    "last_used_at": last_used_at,
                }
            )
    return api_keys


def build_invitation_pool(
    orgs: list[dict],
    org_member_map: dict[str, list[str]],
    users: list[dict],
    rng: random.Random,
) -> list[dict]:
    _require_faker()
    fake = _fake()
    invitations: list[dict] = []
    users_by_id = {user["id"]: user for user in users}
    for org in orgs:
        member_emails = {
            users_by_id[user_id]["email"].lower() for user_id in org_member_map[org["id"]]
        }
        count = _bounded_count(rng, 0, 5, 1.5)
        for _ in range(count):
            invited_email = fake.email().lower()
            while invited_email in member_emails:
                invited_email = fake.email().lower()
            accepted_at = None
            if rng.random() < 0.40:
                accepted_at = _iso(_past_timestamp(rng, days_back=180))
            invitations.append(
                {
                    "id": _deterministic_uuid(rng),
                    "org_id": org["id"],
                    "invited_email": invited_email,
                    "role": _weighted_choice(rng, INVITATION_ROLE_CHOICES),
                    "invited_by": rng.choice(org_member_map[org["id"]]),
                    "expires_at": _iso(_future_timestamp(rng)),
                    "accepted_at": accepted_at,
                }
            )
    return invitations


def validate_dataset(dataset: dict) -> ValidationReport:
    violations: list[str] = []
    counts = {entity: len(dataset.get(entity, [])) for entity in ENTITY_ORDER}
    organizations = dataset.get("organizations", [])
    users_list = dataset.get("users", [])
    orgs = {row["id"]: row for row in organizations}
    users = {row["id"]: row for row in users_list}
    memberships = dataset.get("memberships", [])
    projects_list = dataset.get("projects", [])
    projects = {row["id"]: row for row in projects_list}
    api_keys = dataset.get("api_keys", [])
    invitations = dataset.get("invitations", [])
    membership_ids = {row["id"] for row in memberships}
    api_key_ids = {row["id"] for row in api_keys}
    invitation_ids = {row["id"] for row in invitations}

    org_members: dict[str, set[str]] = {}
    member_emails: dict[str, set[str]] = {}
    membership_joined_at: dict[tuple[str, str], datetime] = {}
    seen_emails: set[str] = set()
    seen_org_ids: set[str] = set()
    seen_key_prefixes: set[str] = set()

    for entity, count in counts.items():
        minimum = _minimum_row_count(entity)
        if count < minimum:
            violations.append(f"row count below minimum for {entity}: {count} < {minimum}")

    for org in organizations:
        if org["id"] in seen_org_ids:
            violations.append(f"duplicate organizations.id: {org['id']}")
        seen_org_ids.add(org["id"])

    for user in users.values():
        email = user["email"].lower()
        if email in seen_emails:
            violations.append(f"duplicate user.email: {email}")
        seen_emails.add(email)

    for membership in memberships:
        org = orgs.get(membership["org_id"])
        user = users.get(membership["user_id"])
        if org is None:
            violations.append(f"membership missing org: {membership['id']}")
            continue
        if user is None:
            violations.append(f"membership missing user: {membership['id']}")
            continue
        org_members.setdefault(org["id"], set()).add(user["id"])
        member_emails.setdefault(org["id"], set()).add(user["email"].lower())
        joined_at = datetime.fromisoformat(membership["joined_at"].replace("Z", "+00:00"))
        membership_joined_at[(org["id"], user["id"])] = joined_at
        org_created = datetime.fromisoformat(org["created_at"].replace("Z", "+00:00"))
        if joined_at < org_created:
            violations.append(f"Rule A violated by membership {membership['id']}")
        invited_by = membership.get("invited_by")
        if invited_by is not None and invited_by not in users:
            violations.append(f"membership invited_by missing user: {membership['id']}")

    for project in projects.values():
        org = orgs.get(project["org_id"])
        if org is None:
            violations.append(f"project missing org: {project['id']}")
            continue
        project_created = datetime.fromisoformat(project["created_at"].replace("Z", "+00:00"))
        org_created = datetime.fromisoformat(org["created_at"].replace("Z", "+00:00"))
        if project_created < org_created:
            violations.append(f"Rule B violated by project {project['id']}")
        if project["created_by"] not in org_members.get(project["org_id"], set()):
            violations.append(f"Rule C violated by project {project['id']}")

    for event in dataset.get("audit_events", []):
        org = orgs.get(event["org_id"])
        project = projects.get(event["project_id"])
        if org is None:
            violations.append(f"audit event missing org: {event['id']}")
            continue
        if project is None:
            violations.append(f"audit event missing project: {event['id']}")
            continue
        if event["user_id"] not in org_members.get(event["org_id"], set()):
            violations.append(f"Rule D violated by audit event {event['id']}")
        if project["org_id"] != event["org_id"]:
            violations.append(f"Rule E violated by audit event {event['id']}")
        event_ts = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        project_created = datetime.fromisoformat(project["created_at"].replace("Z", "+00:00"))
        if event_ts < project_created:
            violations.append(f"Rule F violated by audit event {event['id']}")
        joined_at = membership_joined_at.get((event["org_id"], event["user_id"]))
        if joined_at is not None and event_ts < joined_at:
            violations.append(f"audit event before membership joined_at: {event['id']}")
        resource_type = event["resource_type"]
        resource_id = event["resource_id"]
        if resource_type == "project" and resource_id not in projects:
            violations.append(f"audit event resource project missing: {event['id']}")
        elif resource_type == "user" and resource_id not in users:
            violations.append(f"audit event resource user missing: {event['id']}")
        elif resource_type == "membership" and resource_id not in membership_ids:
            violations.append(f"audit event resource membership missing: {event['id']}")
        elif resource_type == "api_key" and resource_id not in api_key_ids:
            violations.append(f"audit event resource api_key missing: {event['id']}")
        elif resource_type == "invitation" and resource_id not in invitation_ids:
            violations.append(f"audit event resource invitation missing: {event['id']}")

    for api_key in api_keys:
        if api_key["created_by"] not in org_members.get(api_key["org_id"], set()):
            violations.append(f"Rule G violated by api_key {api_key['id']}")
        prefix = api_key["key_prefix"]
        if prefix in seen_key_prefixes:
            violations.append(f"duplicate api_key.key_prefix: {prefix}")
        seen_key_prefixes.add(prefix)
        if api_key["last_used_at"] is not None:
            created_at = datetime.fromisoformat(api_key["created_at"].replace("Z", "+00:00"))
            last_used_at = datetime.fromisoformat(
                api_key["last_used_at"].replace("Z", "+00:00")
            )
            if last_used_at < created_at:
                violations.append(f"api_key last_used_at before created_at: {api_key['id']}")

    for invitation in invitations:
        if invitation["invited_by"] not in org_members.get(invitation["org_id"], set()):
            violations.append(f"Rule H violated by invitation {invitation['id']}")
        invited_email = invitation["invited_email"].lower()
        if invited_email in member_emails.get(invitation["org_id"], set()):
            violations.append(f"Rule I violated by invitation {invitation['id']}")
        expires_at = datetime.fromisoformat(invitation["expires_at"].replace("Z", "+00:00"))
        if expires_at <= BASE_TIME:
            violations.append(f"invitation expiry must be in the future: {invitation['id']}")
        accepted_at = invitation.get("accepted_at")
        if accepted_at is not None:
            accepted_dt = datetime.fromisoformat(accepted_at.replace("Z", "+00:00"))
            if accepted_dt > BASE_TIME:
                violations.append(f"invitation accepted_at must be in the past: {invitation['id']}")

    return ValidationReport(
        ok=not violations,
        violations=violations,
        counts=counts,
        seed=int(dataset.get("seed", -1)),
        profile=str(dataset.get("profile", "unknown")),
    )


def generate_dataset(profile: Profile) -> dict:
    _require_faker()
    global _ACTIVE_FAKER
    Faker.seed(profile.seed)
    _ACTIVE_FAKER = Faker()
    rng = random.Random(profile.seed)

    organizations = build_org_pool(profile, rng)
    users = build_user_pool(profile, rng)
    memberships, org_member_map = build_membership_pool(organizations, users, rng)
    projects, project_org_map = build_project_pool(organizations, org_member_map, rng)
    api_keys = build_api_key_pool(organizations, org_member_map, rng)
    invitations = build_invitation_pool(organizations, org_member_map, users, rng)
    audit_events = build_audit_event_pool(
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
    report = validate_dataset(dataset)
    dataset["report"] = report
    if not report.ok:
        raise ValueError("generated dataset failed validation")
    return dataset


def write_jsonl(dataset: dict, output_dir: Path, profile_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for entity in ENTITY_ORDER:
        path = output_dir / f"{entity}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for chunk in _chunked(dataset.get(entity, []), 1000):
                for row in chunk:
                    handle.write(json.dumps(row, sort_keys=True))
                    handle.write("\n")
    report_path = output_dir / f"{profile_name}-report.json"
    report_payload = dataset["report"].__dict__ if isinstance(dataset.get("report"), ValidationReport) else dataset.get("report", {})
    report_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(dataset: dict, output_dir: Path, profile_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for entity in ENTITY_ORDER:
        rows = dataset.get(entity, [])
        path = output_dir / f"{entity}.csv"
        fieldnames = list(rows[0].keys()) if rows else []
        with path.open("w", encoding="utf-8", newline="") as handle:
            if not fieldnames:
                handle.write("")
                continue
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for chunk in _chunked(rows, 1000):
                writer.writerows(chunk)
    report_path = output_dir / f"{profile_name}-report.csv"
    report = dataset["report"]
    with report_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["profile", "seed", "ok", "entity", "count"])
        for entity in ENTITY_ORDER:
            writer.writerow([report.profile, report.seed, report.ok, entity, report.counts[entity]])


if __name__ == "__main__":
    import sys

    profile_name = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    profiles = {
        "smoke": Profile.SMOKE(),
        "small": Profile.SMALL(),
        "medium": Profile.MEDIUM(),
        "large": Profile.LARGE(),
    }
    profile = profiles[profile_name]
    dataset = generate_dataset(profile)
    print(dataset["report"])
