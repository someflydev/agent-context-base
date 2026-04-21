export interface User {
  id: string;
  email: string;
  display_name: string;
  tenant_id: string | null;
  is_active: boolean;
  acl_ver: number;
  created_at: string;
}

export interface Tenant {
  id: string;
  slug: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface Membership {
  id: string;
  user_id: string;
  tenant_id: string;
  tenant_role: "super_admin" | "tenant_admin" | "tenant_member";
  is_active: boolean;
  created_at: string;
}

export interface Group {
  id: string;
  tenant_id: string;
  slug: string;
  name: string;
  created_at: string;
}

export interface Permission {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

export interface GroupPermission {
  id: string;
  group_id: string;
  permission_id: string;
  granted_at: string;
}

export interface UserGroup {
  id: string;
  user_id: string;
  group_id: string;
  joined_at: string;
}
