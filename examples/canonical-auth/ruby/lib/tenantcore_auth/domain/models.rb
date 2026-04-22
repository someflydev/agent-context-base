require "time"

module TenantcoreAuth
  module Domain
    User = Struct.new(
      :id, :email, :display_name, :tenant_id, :created_at, :is_active, :acl_ver,
      keyword_init: true
    )

    Tenant = Struct.new(
      :id, :slug, :name, :created_at, :is_active,
      keyword_init: true
    )

    Group = Struct.new(
      :id, :tenant_id, :slug, :name, :created_at,
      keyword_init: true
    )

    Permission = Struct.new(
      :id, :name, :description, :created_at,
      keyword_init: true
    )

    Membership = Struct.new(
      :id, :user_id, :tenant_id, :tenant_role, :created_at, :is_active,
      keyword_init: true
    )

    GroupPermission = Struct.new(
      :id, :group_id, :permission_id, :granted_at,
      keyword_init: true
    )

    UserGroup = Struct.new(
      :id, :user_id, :group_id, :joined_at,
      keyword_init: true
    )
  end
end
