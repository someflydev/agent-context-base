require "jwt"
require "openssl"
require "securerandom"

module TenantcoreAuth
  module Auth
    class TokenService
      ISSUER = "tenantcore-auth".freeze
      AUDIENCE = "tenantcore-api".freeze
      EXPIRY_SECONDS = 900

      def initialize(signing_key: nil)
        @signing_key = signing_key || self.class.signing_key
      end

      def issue_token(user, store)
        membership = store.get_active_membership(user.id)
        raise ArgumentError, "No active membership for #{user.id}" unless membership

        tenant_role = membership.tenant_role
        tenant_id = membership.tenant_id
        permissions =
          if tenant_role == "super_admin"
            store.admin_permissions
          else
            store.get_effective_permissions(user.id)
          end
        groups =
          if tenant_id
            store.get_groups_for_user(user.id, tenant_id).map(&:slug)
          else
            []
          end
        now = Time.now.to_i

        payload = {
          "iss" => ISSUER,
          "aud" => AUDIENCE,
          "sub" => user.id,
          "exp" => now + EXPIRY_SECONDS,
          "iat" => now,
          "nbf" => now,
          "jti" => SecureRandom.uuid,
          "tenant_id" => tenant_id,
          "tenant_role" => tenant_role,
          "groups" => groups,
          "permissions" => permissions,
          "acl_ver" => user.acl_ver
        }

        JWT.encode(payload, @signing_key, self.class.algorithm)
      end

      def verify_token(token)
        payload, _header = JWT.decode(
          token,
          self.class.verification_key,
          true,
          algorithm: self.class.algorithm,
          algorithms: [self.class.algorithm],
          iss: ISSUER,
          verify_iss: true,
          aud: AUDIENCE,
          verify_aud: true,
          verify_iat: true,
          verify_jti: true,
          verify_not_before: true,
          required_claims: %w[iss aud sub exp iat nbf jti tenant_role permissions acl_ver]
        )
        payload
      end

      def self.algorithm
        ENV["TENANTCORE_TEST_SECRET"] ? "HS256" : "RS256"
      end

      def self.signing_key
        return ENV["TENANTCORE_TEST_SECRET"] if ENV["TENANTCORE_TEST_SECRET"]

        @signing_key ||= OpenSSL::PKey::RSA.generate(2048)
      end

      def self.verification_key
        return ENV["TENANTCORE_TEST_SECRET"] if ENV["TENANTCORE_TEST_SECRET"]

        signing_key.public_key
      end
    end
  end
end
