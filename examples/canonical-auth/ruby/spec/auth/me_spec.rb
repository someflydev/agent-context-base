require "spec_helper"

RSpec.describe "GET /me" do
  let(:store) { TenantcoreAuth::Domain::InMemoryStore.load_from_fixtures }
  let(:service) { TenantcoreAuth::Auth::TokenService.new }

  def auth_header_for(email)
    user = store.get_user_by_email(email)
    { "HTTP_AUTHORIZATION" => "Bearer #{service.issue_token(user, store)}" }
  end

  it "returns the required response fields" do
    get "/me", {}, auth_header_for("admin@acme.example")

    expect(last_response.status).to eq(200)
    body = JSON.parse(last_response.body)
    expect(body.keys).to include(
      "sub", "email", "display_name", "tenant_id", "tenant_name", "tenant_role",
      "groups", "permissions", "acl_ver", "allowed_routes", "guide_sections",
      "issued_at", "expires_at"
    )
  end

  it "filters allowed_routes by permissions" do
    get "/me", {}, auth_header_for("bob@acme.example")

    body = JSON.parse(last_response.body)
    allowed_paths = body.fetch("allowed_routes").map { |route| route.fetch("path") }
    expect(allowed_paths).to include("/users")
    expect(allowed_paths).not_to include("/admin/tenants")
  end

  it "returns the super admin /me shape" do
    get "/me", {}, auth_header_for("superadmin@tenantcore.dev")

    body = JSON.parse(last_response.body)
    expect(body["tenant_role"]).to eq("super_admin")
    expect(body["tenant_id"]).to be_nil
    expect(body["groups"]).to eq([])
    expect(body.fetch("allowed_routes").map { |route| route["path"] }).to include("/admin/tenants")
    expect(body.fetch("allowed_routes").map { |route| route["path"] }).not_to include("/users")
  end
end
