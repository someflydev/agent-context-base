module TenantcoreAuth
  module Auth
    if defined?(Data)
      AuthContext = Data.define(
        :sub, :email, :tenant_id, :tenant_role,
        :groups, :permissions, :acl_ver,
        :issued_at, :expires_at
      ) do
        def has_permission?(permission)
          permissions.include?(permission)
        end
      end
    else
      AuthContext = Struct.new(
        :sub, :email, :tenant_id, :tenant_role,
        :groups, :permissions, :acl_ver,
        :issued_at, :expires_at,
        keyword_init: true
      ) do
        def has_permission?(permission)
          permissions.include?(permission)
        end
      end
    end
  end
end
