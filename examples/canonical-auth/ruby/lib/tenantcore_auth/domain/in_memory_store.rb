require "json"
require "pathname"
require "securerandom"
require "set"

require_relative "models"

module TenantcoreAuth
  module Domain
    class InMemoryStore
      CANONICAL_PERMISSION_NAMES = [
        "iam:user:read",
        "iam:user:create",
        "iam:user:update",
        "iam:user:delete",
        "iam:user:invite",
        "iam:group:read",
        "iam:group:create",
        "iam:group:update",
        "iam:group:delete",
        "iam:group:assign_permission",
        "iam:group:assign_user",
        "iam:tenant:read",
        "iam:tenant:create",
        "iam:tenant:update",
        "iam:permission:read",
        "billing:invoice:read",
        "billing:invoice:create",
        "billing:subscription:read",
        "billing:subscription:update",
        "reports:usage:read",
        "reports:usage:export",
        "reports:audit:read",
        "admin:tenant:create",
        "admin:tenant:suspend",
        "admin:audit:read"
      ].freeze

      def self.default_fixture_dir
        Pathname.new(__dir__).join("..", "..", "..", "..", "domain", "fixtures").expand_path
      end

      def self.load_from_fixtures(fixture_dir = default_fixture_dir)
        fixture_path = Pathname.new(fixture_dir)
        users = load_collection(fixture_path.join("users.json"), User)
        tenants = load_collection(fixture_path.join("tenants.json"), Tenant)
        groups = load_collection(fixture_path.join("groups.json"), Group)
        permissions = load_collection(fixture_path.join("permissions.json"), Permission)
        memberships = load_collection(fixture_path.join("memberships.json"), Membership)
        group_permissions = load_collection(fixture_path.join("group_permissions.json"), GroupPermission)
        user_groups = load_collection(fixture_path.join("user_groups.json"), UserGroup)

        new(
          users: users,
          tenants: tenants,
          groups: groups,
          permissions: permissions,
          memberships: memberships,
          group_permissions: group_permissions,
          user_groups: user_groups
        ).tap(&:seed_canonical_permissions!)
      end

      def self.load_collection(path, struct_class)
        JSON.parse(path.read, symbolize_names: true).map do |row|
          normalized = row.transform_values do |value|
            value.is_a?(String) && value.match?(/\A\d{4}-\d{2}-\d{2}T/) ? Time.iso8601(value) : value
          end
          struct_class.new(**normalized)
        end
      end

      attr_reader :users, :tenants, :groups, :permissions, :memberships, :group_permissions, :user_groups

      def initialize(users:, tenants:, groups:, permissions:, memberships:, group_permissions:, user_groups:)
        @users = users
        @tenants = tenants
        @groups = groups
        @permissions = permissions
        @memberships = memberships
        @group_permissions = group_permissions
        @user_groups = user_groups
        refresh_indexes!
      end

      def get_user_by_id(id)
        @users_by_id[id]
      end

      def get_user_by_email(email)
        @users_by_email[email]
      end

      def get_tenant_by_id(id)
        @tenants_by_id[id]
      end

      def get_tenant_name(id)
        get_tenant_by_id(id)&.name
      end

      def get_group_by_id(id)
        @groups_by_id[id]
      end

      def get_permission_by_name(name)
        @permissions_by_name[name]
      end

      def get_active_membership(user_id)
        @memberships.find { |membership| membership.user_id == user_id && membership.is_active }
      end

      def verify_membership(user_id, tenant_id)
        @memberships.any? do |membership|
          membership.user_id == user_id && membership.tenant_id == tenant_id && membership.is_active
        end
      end

      def get_membership_role(user_id, tenant_id = nil)
        membership = @memberships.find do |row|
          row.user_id == user_id && row.tenant_id == tenant_id && row.is_active
        end
        membership&.tenant_role
      end

      def get_groups_for_user(user_id, tenant_id)
        group_ids = @user_groups.select { |row| row.user_id == user_id }.map(&:group_id)
        group_ids.map do |group_id|
          group = @groups_by_id[group_id]
          group if group && group.tenant_id == tenant_id
        end.compact
      end

      def get_effective_permissions(user_id)
        membership = get_active_membership(user_id)
        return [] unless membership

        case membership.tenant_role
        when "tenant_admin"
          @permissions.map(&:name).sort
        when "super_admin"
          admin_permissions
        else
          group_ids = @user_groups.select { |row| row.user_id == user_id }.map(&:group_id).to_set
          @group_permissions.map do |row|
            @permissions_by_id[row.permission_id]&.name if group_ids.include?(row.group_id)
          end.compact.uniq.sort
        end
      end

      def admin_permissions
        @permissions.map(&:name).grep(/\Aadmin:/).sort
      end

      def list_users(tenant_id)
        @users.select { |user| user.tenant_id == tenant_id }.sort_by(&:email)
      end

      def list_groups(tenant_id)
        @groups.select { |group| group.tenant_id == tenant_id }.sort_by(&:slug)
      end

      def list_permissions
        @permissions.sort_by(&:name)
      end

      def list_tenants
        @tenants.sort_by(&:slug)
      end

      def invite_user(tenant_id:, email:, display_name:, group_slugs: [])
        user = User.new(
          id: "u-#{SecureRandom.uuid}",
          email: email,
          display_name: display_name,
          tenant_id: tenant_id,
          created_at: Time.now.utc,
          is_active: true,
          acl_ver: 1
        )
        @users << user
        @memberships << Membership.new(
          id: "m-#{SecureRandom.uuid}",
          user_id: user.id,
          tenant_id: tenant_id,
          tenant_role: "tenant_member",
          created_at: Time.now.utc,
          is_active: true
        )
        group_slugs.each do |slug|
          group = @groups.find { |row| row.slug == slug && row.tenant_id == tenant_id }
          next unless group

          @user_groups << UserGroup.new(
            id: "ug-#{SecureRandom.uuid}",
            user_id: user.id,
            group_id: group.id,
            joined_at: Time.now.utc
          )
        end
        refresh_indexes!
        user
      end

      def create_group(tenant_id:, slug:, name:, permission_names: [])
        group = Group.new(
          id: "g-#{SecureRandom.uuid}",
          tenant_id: tenant_id,
          slug: slug,
          name: name,
          created_at: Time.now.utc
        )
        @groups << group
        permission_names.each do |permission_name|
          assign_permission_to_group(group.id, permission_name, tenant_id)
        end
        refresh_indexes!
        group
      end

      def assign_permission_to_group(group_id, permission_name, tenant_id)
        group = @groups_by_id[group_id]
        permission = @permissions_by_name[permission_name]
        return false unless group && permission
        return false unless group.tenant_id == tenant_id

        already_assigned = @group_permissions.any? do |row|
          row.group_id == group_id && row.permission_id == permission.id
        end
        return true if already_assigned

        @group_permissions << GroupPermission.new(
          id: "gp-#{SecureRandom.uuid}",
          group_id: group_id,
          permission_id: permission.id,
          granted_at: Time.now.utc
        )
        true
      end

      def assign_user_to_group(group_id, user_id, tenant_id)
        group = @groups_by_id[group_id]
        user = @users_by_id[user_id]
        return false unless group && user
        return false unless group.tenant_id == tenant_id && user.tenant_id == tenant_id

        already_assigned = @user_groups.any? { |row| row.group_id == group_id && row.user_id == user_id }
        return true if already_assigned

        @user_groups << UserGroup.new(
          id: "ug-#{SecureRandom.uuid}",
          user_id: user_id,
          group_id: group_id,
          joined_at: Time.now.utc
        )
        true
      end

      def create_tenant(slug:, name:, first_admin_email:)
        tenant = Tenant.new(
          id: "t-#{SecureRandom.uuid}",
          slug: slug,
          name: name,
          created_at: Time.now.utc,
          is_active: true
        )
        @tenants << tenant
        admin = User.new(
          id: "u-#{SecureRandom.uuid}",
          email: first_admin_email,
          display_name: "#{name} Admin",
          tenant_id: tenant.id,
          created_at: Time.now.utc,
          is_active: true,
          acl_ver: 1
        )
        @users << admin
        @memberships << Membership.new(
          id: "m-#{SecureRandom.uuid}",
          user_id: admin.id,
          tenant_id: tenant.id,
          tenant_role: "tenant_admin",
          created_at: Time.now.utc,
          is_active: true
        )
        refresh_indexes!
        tenant
      end

      def seed_canonical_permissions!
        existing = @permissions.map(&:name).to_set
        CANONICAL_PERMISSION_NAMES.each do |permission_name|
          next if existing.include?(permission_name)

          @permissions << Permission.new(
            id: "perm-#{permission_name.tr(':', '-')}",
            name: permission_name,
            description: "Canonical seeded permission",
            created_at: Time.iso8601("2025-01-01T00:00:00Z")
          )
        end
        refresh_indexes!
      end

      private

      def refresh_indexes!
        @users_by_id = @users.to_h { |row| [row.id, row] }
        @users_by_email = @users.to_h { |row| [row.email, row] }
        @tenants_by_id = @tenants.to_h { |row| [row.id, row] }
        @groups_by_id = @groups.to_h { |row| [row.id, row] }
        @permissions_by_id = @permissions.to_h { |row| [row.id, row] }
        @permissions_by_name = @permissions.to_h { |row| [row.name, row] }
      end
    end
  end
end
