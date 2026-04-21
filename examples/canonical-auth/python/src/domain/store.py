import json
from pathlib import Path
from typing import Optional

from .models import User, Tenant, Membership, Group, Permission, GroupPermission, UserGroup

FIXTURES_DIR = Path(__file__).parent.parent.parent.parent / "domain" / "fixtures"

class InMemoryStore:
    def __init__(self):
        self.users: list[User] = []
        self.tenants: list[Tenant] = []
        self.memberships: list[Membership] = []
        self.groups: list[Group] = []
        self.permissions: list[Permission] = []
        self.group_permissions: list[GroupPermission] = []
        self.user_groups: list[UserGroup] = []
        self._load_fixtures()

    def _load_fixtures(self):
        def load_json(filename):
            with open(FIXTURES_DIR / filename, "r") as f:
                return json.load(f)

        self.users = [User(**u) for u in load_json("users.json")]
        self.tenants = [Tenant(**t) for t in load_json("tenants.json")]
        self.memberships = [Membership(**m) for m in load_json("memberships.json")]
        self.groups = [Group(**g) for g in load_json("groups.json")]
        self.permissions = [Permission(**p) for p in load_json("permissions.json")]
        self.group_permissions = [GroupPermission(**gp) for gp in load_json("group_permissions.json")]
        self.user_groups = [UserGroup(**ug) for ug in load_json("user_groups.json")]

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return next((u for u in self.users if u.id == user_id), None)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self.users if u.email == email), None)

    def get_tenant_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return next((t for t in self.tenants if t.id == tenant_id), None)

    def get_groups_for_user(self, user_id: str, tenant_id: Optional[str]) -> list[Group]:
        """Return groups for a user, constrained by tenant context."""
        user_group_ids = {ug.group_id for ug in self.user_groups if ug.user_id == user_id}
        if tenant_id:
            return [g for g in self.groups if g.id in user_group_ids and g.tenant_id == tenant_id]
        return [g for g in self.groups if g.id in user_group_ids]

    def get_effective_permissions(self, user_id: str) -> list[str]:
        """Return a list of permission names the user has via their groups."""
        user_group_ids = {ug.group_id for ug in self.user_groups if ug.user_id == user_id}
        permission_ids = {
            gp.permission_id for gp in self.group_permissions if gp.group_id in user_group_ids
        }
        return [p.name for p in self.permissions if p.id in permission_ids]

    def verify_membership(self, user_id: str, tenant_id: str) -> bool:
        """Verify the user has an active membership in the tenant."""
        m = next(
            (m for m in self.memberships if m.user_id == user_id and m.tenant_id == tenant_id),
            None
        )
        return m is not None and m.is_active

    def get_tenant_name(self, tenant_id: str) -> Optional[str]:
        t = self.get_tenant_by_id(tenant_id)
        return t.name if t else None
