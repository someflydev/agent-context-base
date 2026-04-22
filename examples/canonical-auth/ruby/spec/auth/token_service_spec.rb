require "spec_helper"

RSpec.describe TenantcoreAuth::Auth::TokenService do
  let(:store) { TenantcoreAuth::Domain::InMemoryStore.load_from_fixtures }
  let(:service) { described_class.new }

  it "produces a decodable JWT with the canonical claims" do
    user = store.get_user_by_email("admin@acme.example")
    token = service.issue_token(user, store)
    claims = service.verify_token(token)

    expect(claims).to include("iss", "aud", "sub", "exp", "iat", "nbf", "jti", "tenant_role", "permissions", "acl_ver")
    expect(claims["iss"]).to eq("tenantcore-auth")
    expect(claims["aud"]).to eq("tenantcore-api")
    expect(claims["sub"]).to eq(user.id)
  end

  it "expires within fifteen minutes" do
    user = store.get_user_by_email("admin@acme.example")
    claims = service.verify_token(service.issue_token(user, store))

    expect(claims["exp"] - claims["iat"]).to eq(900)
  end

  it "embeds the effective permissions from the store" do
    user = store.get_user_by_email("alice@acme.example")
    claims = service.verify_token(service.issue_token(user, store))

    expect(claims["permissions"]).to match_array(store.get_effective_permissions(user.id))
  end
end
