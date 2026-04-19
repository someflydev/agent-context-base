from __future__ import annotations

import json
from pathlib import Path


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
CREATED_AT = "2025-01-01T00:00:00Z"
GRANTED_AT = "2025-01-02T00:00:00Z"
JOINED_AT = "2025-01-03T00:00:00Z"


def write_json(name: str, payload: list[dict[str, object]]) -> None:
    path = FIXTURES_DIR / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_tenants() -> list[dict[str, object]]:
    return [
        {
            "created_at": CREATED_AT,
            "id": "t-acme-0001",
            "is_active": True,
            "name": "Acme Corp",
            "slug": "acme",
        },
        {
            "created_at": CREATED_AT,
            "id": "t-globex-0001",
            "is_active": True,
            "name": "Globex Industries",
            "slug": "globex",
        },
    ]


def build_users() -> list[dict[str, object]]:
    return [
        {
            "acl_ver": 1,
            "created_at": CREATED_AT,
            "display_name": "Super Admin",
            "email": "superadmin@tenantcore.dev",
            "id": "u-super-0001",
            "is_active": True,
            "tenant_id": None,
        },
        {
            "acl_ver": 1,
            "created_at": CREATED_AT,
            "display_name": "Acme Admin",
            "email": "admin@acme.example",
            "id": "u-acme-admin-0001",
            "is_active": True,
            "tenant_id": "t-acme-0001",
        },
        {
            "acl_ver": 1,
            "created_at": CREATED_AT,
            "display_name": "Alice Member",
            "email": "alice@acme.example",
            "id": "u-acme-member-0001",
            "is_active": True,
            "tenant_id": "t-acme-0001",
        },
        {
            "acl_ver": 1,
            "created_at": CREATED_AT,
            "display_name": "Bob Member",
            "email": "bob@acme.example",
            "id": "u-acme-member-0002",
            "is_active": True,
            "tenant_id": "t-acme-0001",
        },
        {
            "acl_ver": 1,
            "created_at": CREATED_AT,
            "display_name": "Globex Admin",
            "email": "admin@globex.example",
            "id": "u-globex-admin-0001",
            "is_active": True,
            "tenant_id": "t-globex-0001",
        },
        {
            "acl_ver": 1,
            "created_at": CREATED_AT,
            "display_name": "Carol Member",
            "email": "carol@globex.example",
            "id": "u-globex-member-0001",
            "is_active": True,
            "tenant_id": "t-globex-0001",
        },
    ]


def build_memberships() -> list[dict[str, object]]:
    return [
        {
            "created_at": CREATED_AT,
            "id": "m-super-0001",
            "is_active": True,
            "tenant_id": None,
            "tenant_role": "super_admin",
            "user_id": "u-super-0001",
        },
        {
            "created_at": CREATED_AT,
            "id": "m-acme-admin-0001",
            "is_active": True,
            "tenant_id": "t-acme-0001",
            "tenant_role": "tenant_admin",
            "user_id": "u-acme-admin-0001",
        },
        {
            "created_at": CREATED_AT,
            "id": "m-acme-member-0001",
            "is_active": True,
            "tenant_id": "t-acme-0001",
            "tenant_role": "tenant_member",
            "user_id": "u-acme-member-0001",
        },
        {
            "created_at": CREATED_AT,
            "id": "m-acme-member-0002",
            "is_active": True,
            "tenant_id": "t-acme-0001",
            "tenant_role": "tenant_member",
            "user_id": "u-acme-member-0002",
        },
        {
            "created_at": CREATED_AT,
            "id": "m-globex-admin-0001",
            "is_active": True,
            "tenant_id": "t-globex-0001",
            "tenant_role": "tenant_admin",
            "user_id": "u-globex-admin-0001",
        },
        {
            "created_at": CREATED_AT,
            "id": "m-globex-member-0001",
            "is_active": True,
            "tenant_id": "t-globex-0001",
            "tenant_role": "tenant_member",
            "user_id": "u-globex-member-0001",
        },
    ]


def build_groups() -> list[dict[str, object]]:
    return [
        {
            "created_at": CREATED_AT,
            "id": "g-acme-iam-0001",
            "name": "IAM Admins",
            "slug": "iam-admins",
            "tenant_id": "t-acme-0001",
        },
        {
            "created_at": CREATED_AT,
            "id": "g-acme-billing-0001",
            "name": "Billing Readers",
            "slug": "billing-readers",
            "tenant_id": "t-acme-0001",
        },
        {
            "created_at": CREATED_AT,
            "id": "g-globex-reports-0001",
            "name": "Report Viewers",
            "slug": "report-viewers",
            "tenant_id": "t-globex-0001",
        },
    ]


def build_permissions() -> list[dict[str, object]]:
    minimum_catalog = [
        ("perm-iam-user-read", "iam:user:read", "Read tenant users"),
        ("perm-iam-user-create", "iam:user:create", "Create tenant users"),
        ("perm-iam-user-invite", "iam:user:invite", "Invite tenant users"),
        ("perm-iam-group-read", "iam:group:read", "Read tenant groups"),
        ("perm-iam-group-create", "iam:group:create", "Create tenant groups"),
        (
            "perm-iam-group-assign-permission",
            "iam:group:assign_permission",
            "Assign catalog permissions to tenant groups",
        ),
        (
            "perm-iam-group-assign-user",
            "iam:group:assign_user",
            "Assign tenant users to groups",
        ),
        ("perm-iam-permission-read", "iam:permission:read", "Read permission catalog"),
        ("perm-billing-invoice-read", "billing:invoice:read", "Read invoices"),
        ("perm-reports-usage-read", "reports:usage:read", "Read usage reports"),
    ]
    return [
        {
            "created_at": CREATED_AT,
            "description": description,
            "id": perm_id,
            "name": name,
        }
        for perm_id, name, description in minimum_catalog
    ]


def build_group_permissions() -> list[dict[str, object]]:
    assignments = [
        ("gp-acme-iam-01", "g-acme-iam-0001", "perm-iam-user-read"),
        ("gp-acme-iam-02", "g-acme-iam-0001", "perm-iam-user-create"),
        ("gp-acme-iam-03", "g-acme-iam-0001", "perm-iam-user-invite"),
        ("gp-acme-iam-04", "g-acme-iam-0001", "perm-iam-group-read"),
        ("gp-acme-iam-05", "g-acme-iam-0001", "perm-iam-group-create"),
        ("gp-acme-iam-06", "g-acme-iam-0001", "perm-iam-group-assign-permission"),
        ("gp-acme-iam-07", "g-acme-iam-0001", "perm-iam-group-assign-user"),
        ("gp-acme-iam-08", "g-acme-iam-0001", "perm-iam-permission-read"),
        ("gp-acme-billing-01", "g-acme-billing-0001", "perm-iam-user-read"),
        ("gp-acme-billing-02", "g-acme-billing-0001", "perm-billing-invoice-read"),
        ("gp-globex-report-01", "g-globex-reports-0001", "perm-reports-usage-read"),
        ("gp-globex-report-02", "g-globex-reports-0001", "perm-iam-user-read"),
    ]
    return [
        {
            "granted_at": GRANTED_AT,
            "group_id": group_id,
            "id": assignment_id,
            "permission_id": permission_id,
        }
        for assignment_id, group_id, permission_id in assignments
    ]


def build_user_groups() -> list[dict[str, object]]:
    return [
        {
            "group_id": "g-acme-iam-0001",
            "id": "ug-acme-alice-0001",
            "joined_at": JOINED_AT,
            "user_id": "u-acme-member-0001",
        },
        {
            "group_id": "g-acme-billing-0001",
            "id": "ug-acme-bob-0001",
            "joined_at": JOINED_AT,
            "user_id": "u-acme-member-0002",
        },
        {
            "group_id": "g-globex-reports-0001",
            "id": "ug-globex-carol-0001",
            "joined_at": JOINED_AT,
            "user_id": "u-globex-member-0001",
        },
    ]


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    write_json("tenants.json", build_tenants())
    write_json("users.json", build_users())
    write_json("memberships.json", build_memberships())
    write_json("groups.json", build_groups())
    write_json("permissions.json", build_permissions())
    write_json("group_permissions.json", build_group_permissions())
    write_json("user_groups.json", build_user_groups())


if __name__ == "__main__":
    main()
