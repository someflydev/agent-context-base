from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AuthContext:
    sub: str
    email: str
    tenant_id: Optional[str]
    tenant_role: str        # "super_admin" | "tenant_admin" | "tenant_member"
    groups: list[str]
    permissions: list[str]
    acl_ver: int
    issued_at: datetime
    expires_at: datetime

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
