defmodule TenantCore.Organization do
  @enforce_keys [:id, :name, :slug, :plan, :region, :created_at, :owner_email]
  defstruct [:id, :name, :slug, :plan, :region, :created_at, :owner_email]
end

defmodule TenantCore.User do
  @enforce_keys [:id, :email, :full_name, :locale, :timezone, :created_at]
  defstruct [:id, :email, :full_name, :locale, :timezone, :created_at]
end

defmodule TenantCore.Membership do
  @enforce_keys [:id, :org_id, :user_id, :role, :joined_at, :invited_by]
  defstruct [:id, :org_id, :user_id, :role, :joined_at, :invited_by]
end

defmodule TenantCore.Project do
  @enforce_keys [:id, :org_id, :name, :status, :created_by, :created_at]
  defstruct [:id, :org_id, :name, :status, :created_by, :created_at]
end

defmodule TenantCore.AuditEvent do
  @enforce_keys [:id, :org_id, :user_id, :project_id, :action, :resource_type, :resource_id, :ts]
  defstruct [:id, :org_id, :user_id, :project_id, :action, :resource_type, :resource_id, :ts]
end

defmodule TenantCore.ApiKey do
  @enforce_keys [:id, :org_id, :created_by, :name, :key_prefix, :created_at, :last_used_at]
  defstruct [:id, :org_id, :created_by, :name, :key_prefix, :created_at, :last_used_at]
end

defmodule TenantCore.Invitation do
  @enforce_keys [:id, :org_id, :invited_email, :role, :invited_by, :expires_at, :accepted_at]
  defstruct [:id, :org_id, :invited_email, :role, :invited_by, :expires_at, :accepted_at]
end
