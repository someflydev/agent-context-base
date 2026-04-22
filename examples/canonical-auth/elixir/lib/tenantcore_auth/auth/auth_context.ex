defmodule TenantcoreAuth.Auth.AuthContext do
  defstruct [:sub, :email, :tenant_id, :tenant_role, :groups, :permissions, :acl_ver, :issued_at, :expires_at]

  def has_permission?(%__MODULE__{permissions: permissions}, permission) do
    permission in permissions
  end
end
