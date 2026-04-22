require "spec_helper"

RSpec.describe TenantcoreAuth::Auth::JwtMiddleware do
  let(:store) { TenantcoreAuth::Domain::InMemoryStore.load_from_fixtures }
  let(:service) { TenantcoreAuth::Auth::TokenService.new }

  it "rejects expired tokens before route logic executes" do
    user = store.get_user_by_email("admin@acme.example")
    token = JWT.encode(
      {
        "iss" => "tenantcore-auth",
        "aud" => "tenantcore-api",
        "sub" => user.id,
        "exp" => Time.now.to_i - 1,
        "iat" => Time.now.to_i - 2,
        "nbf" => Time.now.to_i - 2,
        "jti" => "expired-token",
        "tenant_id" => user.tenant_id,
        "tenant_role" => "tenant_admin",
        "groups" => ["iam-admins"],
        "permissions" => store.get_effective_permissions(user.id),
        "acl_ver" => user.acl_ver
      },
      ENV.fetch("TENANTCORE_TEST_SECRET"),
      "HS256"
    )

    get "/me", {}, { "HTTP_AUTHORIZATION" => "Bearer #{token}" }

    expect(last_response.status).to eq(401)
  end

  it "rejects stale acl_ver tokens" do
    user = store.get_user_by_email("admin@acme.example")
    token = JWT.encode(
      {
        "iss" => "tenantcore-auth",
        "aud" => "tenantcore-api",
        "sub" => user.id,
        "exp" => Time.now.to_i + 60,
        "iat" => Time.now.to_i,
        "nbf" => Time.now.to_i,
        "jti" => "stale-token",
        "tenant_id" => user.tenant_id,
        "tenant_role" => "tenant_admin",
        "groups" => ["iam-admins"],
        "permissions" => store.get_effective_permissions(user.id),
        "acl_ver" => user.acl_ver - 1
      },
      ENV.fetch("TENANTCORE_TEST_SECRET"),
      "HS256"
    )

    get "/me", {}, { "HTTP_AUTHORIZATION" => "Bearer #{token}" }

    expect(last_response.status).to eq(401)
  end
end
