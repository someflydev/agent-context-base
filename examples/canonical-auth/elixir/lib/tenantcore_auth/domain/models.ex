defmodule TenantcoreAuth.Domain.User do
  defstruct [:id, :email, :display_name, :tenant_id, :created_at, :is_active, :acl_ver]
end

defmodule TenantcoreAuth.Domain.Tenant do
  defstruct [:id, :slug, :name, :created_at, :is_active]
end

defmodule TenantcoreAuth.Domain.Group do
  defstruct [:id, :tenant_id, :slug, :name, :created_at]
end

defmodule TenantcoreAuth.Domain.Permission do
  defstruct [:id, :name, :description, :created_at]
end

defmodule TenantcoreAuth.Domain.Membership do
  defstruct [:id, :user_id, :tenant_id, :tenant_role, :created_at, :is_active]
end

defmodule TenantcoreAuth.Domain.GroupPermission do
  defstruct [:id, :group_id, :permission_id, :granted_at]
end

defmodule TenantcoreAuth.Domain.UserGroup do
  defstruct [:id, :user_id, :group_id, :joined_at]
end
