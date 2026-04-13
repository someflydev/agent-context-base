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


def run_factory_graph(
    profile: Profile, output_dir: Path, formats: tuple[str, ...] = ("jsonl",)
) -> ValidationReport:
    if profile.name not in {"smoke", "small"}:
        raise ValueError("factory graph is intended for smoke and small profiles only")

    use_seed(profile.seed)

    org_count = profile.num_orgs
    organizations = OrganizationFactory.create_batch(org_count)
    users = UserFactory.create_batch(profile.num_users, seed=profile.seed)
    memberships: list[dict] = []
    org_member_map: dict[str, list[str]] = {}
    users_by_index = {index: user for index, user in enumerate(users)}

    for org_index, org in enumerate(organizations):
        count = 3 if profile.name == "smoke" else min(10, org.get("initial_member_count", 6))
        member_ids: list[str] = []
        for offset in range(count):
            user = users_by_index[(org_index * count + offset) % len(users)]
            membership = MembershipFactory(org=org, user=user)
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
            project = ProjectFactory(org=org, creator=creator)
            projects.append(project)
            for event_index in range(5 if profile.name == "smoke" else 10):
                actor = org_users[event_index % len(org_users)]
                audit_events.append(AuditEventFactory(org=org, user=actor, project=project))
        api_keys.append(ApiKeyFactory(org=org, creator=org_users[0]))
        invitations.append(InvitationFactory(org=org, inviter=org_users[0]))

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
