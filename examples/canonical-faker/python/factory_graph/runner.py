from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


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


def _load_factories_module():
    module_path = Path(__file__).resolve().with_name("factories.py")
    spec = importlib.util.spec_from_file_location("canonical_faker_factory_graph_factories", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load factory module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


factories = _load_factories_module()
ApiKeyFactory = factories.ApiKeyFactory
AuditEventFactory = factories.AuditEventFactory
InvitationFactory = factories.InvitationFactory
MembershipFactory = factories.MembershipFactory
OrganizationFactory = factories.OrganizationFactory
ProjectFactory = factories.ProjectFactory
UserFactory = factories.UserFactory
use_seed = factories.use_seed


def _summary(report: ValidationReport) -> str:
    payload = {
        "ok": report.ok,
        "profile": report.profile,
        "seed": report.seed,
        "counts": report.counts,
        "violations": report.violations,
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def _canonical_keys() -> dict[str, tuple[str, ...]]:
    return {
        "organizations": (
            "id",
            "name",
            "slug",
            "plan",
            "region",
            "created_at",
            "owner_email",
            "sequence",
        ),
        "users": (
            "id",
            "email",
            "full_name",
            "locale",
            "timezone",
            "created_at",
            "sequence",
        ),
        "memberships": (
            "id",
            "org_id",
            "user_id",
            "role",
            "joined_at",
            "invited_by",
            "user_email",
        ),
        "projects": (
            "id",
            "org_id",
            "name",
            "status",
            "created_by",
            "created_at",
        ),
        "audit_events": (
            "id",
            "org_id",
            "user_id",
            "project_id",
            "action",
            "resource_type",
            "resource_id",
            "ts",
        ),
        "api_keys": (
            "id",
            "org_id",
            "created_by",
            "name",
            "key_prefix",
            "created_at",
            "last_used_at",
        ),
        "invitations": (
            "id",
            "org_id",
            "invited_email",
            "role",
            "invited_by",
            "expires_at",
            "accepted_at",
        ),
    }


def _select_fields(row: dict, entity: str) -> dict:
    return {key: row[key] for key in _canonical_keys()[entity]}


def run_factory_graph(
    profile: Profile, output_dir: Path, formats: tuple[str, ...] = ("jsonl",)
) -> ValidationReport:
    if profile.name not in {"smoke", "small"}:
        raise ValueError("factory graph is intended for smoke and small profiles only")

    use_seed(profile.seed)

    org_count = profile.num_orgs
    raw_organizations = [
        OrganizationFactory(enterprise_org=(profile.name == "small" and index == 0))
        for index in range(org_count)
    ]
    organizations = [_select_fields(row, "organizations") for row in raw_organizations]
    users = [
        _select_fields(row, "users")
        for row in UserFactory.create_batch(profile.num_users, seed=profile.seed)
    ]
    memberships: list[dict] = []
    org_member_map: dict[str, list[str]] = {}
    users_by_index = {index: user for index, user in enumerate(users)}

    for org_index, org in enumerate(organizations):
        count = 3 if profile.name == "smoke" else (10 if org["plan"] == "enterprise" else 6)
        member_ids: list[str] = []
        for offset in range(count):
            user = users_by_index[(org_index * count + offset) % len(users)]
            membership = _select_fields(MembershipFactory(org=org, user=user), "memberships")
            if offset == 0:
                membership["role"] = "owner"
                membership["invited_by"] = None
            elif member_ids:
                membership["invited_by"] = member_ids[0]
            memberships.append(membership)
            member_ids.append(user["id"])
        org_member_map[org["id"]] = member_ids

    projects: list[dict] = []
    api_keys: list[dict] = []
    invitations: list[dict] = []
    audit_events: list[dict] = []
    users_by_id = {user["id"]: user for user in users}

    for org_index, org in enumerate(organizations):
        org_users = [users_by_id[user_id] for user_id in org_member_map[org["id"]]]
        for project_index in range(3 if profile.name == "smoke" else 5):
            creator = org_users[project_index % len(org_users)]
            project = _select_fields(ProjectFactory(org=org, creator=creator), "projects")
            projects.append(project)
            for event_index in range(5 if profile.name == "smoke" else 10):
                actor = org_users[event_index % len(org_users)]
                audit_events.append(
                    _select_fields(
                        AuditEventFactory(org=org, user=actor, project=project),
                        "audit_events",
                    )
                )
        api_keys.append(_select_fields(ApiKeyFactory(org=org, creator=org_users[0]), "api_keys"))
        invitations.append(
            _select_fields(InvitationFactory(org=org, inviter=org_users[0]), "invitations")
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
        raise ValueError(_summary(report))
    if "jsonl" in formats:
        domain.write_jsonl(dataset, output_dir, profile.name)
    if "csv" in formats:
        domain.write_csv(dataset, output_dir, profile.name)
    print(_summary(report))
    return report
