require "spec_helper"

RSpec.describe "TenantCore auth integration" do
  let(:store) { TenantcoreAuth::Domain::InMemoryStore.load_from_fixtures }
  let(:service) { TenantcoreAuth::Auth::TokenService.new }

  def auth_header_for(email)
    user = store.get_user_by_email(email)
    { "HTTP_AUTHORIZATION" => "Bearer #{service.issue_token(user, store)}" }
  end

  it "token_issue_success" do
    post "/auth/token", JSON.generate(email: "admin@acme.example", password: "password"), "CONTENT_TYPE" => "application/json"
    expect(last_response.status).to eq(200)
    expect(JSON.parse(last_response.body)).to include("access_token")
  end

  it "token_invalid_credentials" do
    post "/auth/token", JSON.generate(email: "admin@acme.example", password: "wrong"), "CONTENT_TYPE" => "application/json"
    expect(last_response.status).to eq(401)
  end

  it "token_expired_rejection" do
    user = store.get_user_by_email("admin@acme.example")
    token = JWT.encode(
      {
        "iss" => "tenantcore-auth", "aud" => "tenantcore-api", "sub" => user.id,
        "exp" => Time.now.to_i - 1, "iat" => Time.now.to_i - 2, "nbf" => Time.now.to_i - 2,
        "jti" => "expired", "tenant_id" => user.tenant_id, "tenant_role" => "tenant_admin",
        "groups" => ["iam-admins"], "permissions" => store.get_effective_permissions(user.id),
        "acl_ver" => user.acl_ver
      },
      ENV.fetch("TENANTCORE_TEST_SECRET"), "HS256"
    )
    get "/me", {}, "HTTP_AUTHORIZATION" => "Bearer #{token}"
    expect(last_response.status).to eq(401)
  end

  it "token_stale_acl_ver" do
    user = store.get_user_by_email("admin@acme.example")
    token = JWT.encode(
      {
        "iss" => "tenantcore-auth", "aud" => "tenantcore-api", "sub" => user.id,
        "exp" => Time.now.to_i + 60, "iat" => Time.now.to_i, "nbf" => Time.now.to_i,
        "jti" => "stale", "tenant_id" => user.tenant_id, "tenant_role" => "tenant_admin",
        "groups" => ["iam-admins"], "permissions" => store.get_effective_permissions(user.id),
        "acl_ver" => user.acl_ver - 1
      },
      ENV.fetch("TENANTCORE_TEST_SECRET"), "HS256"
    )
    get "/me", {}, "HTTP_AUTHORIZATION" => "Bearer #{token}"
    expect(last_response.status).to eq(401)
  end

  it "get_me_success" do
    get "/me", {}, auth_header_for("admin@acme.example")
    expect(last_response.status).to eq(200)
  end

  it "get_me_unauthorized" do
    get "/me"
    expect(last_response.status).to eq(401)
  end

  it "rbac_permission_granted" do
    get "/users", {}, auth_header_for("admin@acme.example")
    expect(last_response.status).to eq(200)
  end

  it "rbac_permission_denied" do
    post "/groups", JSON.generate(slug: "extra", name: "Extra"), auth_header_for("bob@acme.example").merge("CONTENT_TYPE" => "application/json")
    expect(last_response.status).to eq(403)
  end

  it "cross_tenant_denial" do
    target = store.get_user_by_email("admin@globex.example")
    get "/users/#{target.id}", {}, auth_header_for("admin@acme.example")
    expect(last_response.status).to eq(403)
  end

  it "super_admin_access" do
    get "/admin/tenants", {}, auth_header_for("superadmin@tenantcore.dev")
    expect(last_response.status).to eq(200)
  end

  it "super_admin_tenant_scoped_denial" do
    get "/users", {}, auth_header_for("superadmin@tenantcore.dev")
    expect(last_response.status).to eq(403)
  end

  it "me_allowed_routes_match_permissions" do
    get "/me", {}, auth_header_for("admin@acme.example")
    body = JSON.parse(last_response.body)
    allowed_paths = body.fetch("allowed_routes").map { |route| route.fetch("path") }

    expect(allowed_paths).to include("/users")
    expect(allowed_paths).not_to include("/admin/tenants")
  end
end
