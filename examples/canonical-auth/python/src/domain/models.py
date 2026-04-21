from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    display_name: str
    tenant_id: Optional[str]
    is_active: bool
    acl_ver: int
    created_at: str

@dataclass
class Tenant:
    id: str
    slug: str
    name: str
    is_active: bool
    created_at: str

@dataclass
class Membership:
    id: str
    user_id: str
    tenant_id: str
    tenant_role: str  # "super_admin" | "tenant_admin" | "tenant_member"
    is_active: bool
    created_at: str

@dataclass
class Group:
    id: str
    tenant_id: str
    slug: str
    name: str
    created_at: str

@dataclass
class Permission:
    id: str
    name: str
    description: str
    created_at: str

@dataclass
class GroupPermission:
    id: str
    group_id: str
    permission_id: str
    granted_at: str

@dataclass
class UserGroup:
    id: str
    user_id: str
    group_id: str
    joined_at: str
