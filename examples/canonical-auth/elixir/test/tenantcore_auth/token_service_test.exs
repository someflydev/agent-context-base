defmodule TenantcoreAuth.TokenServiceTest do
  use ExUnit.Case, async: true

  alias TenantcoreAuth.Auth.TokenService
  alias TenantcoreAuth.Domain.InMemoryStore

  setup do
    System.put_env("TENANTCORE_TEST_SECRET", "tenantcore-test-secret")
    :ok
  end

  test "issue_token produces the required claims" do
    user = InMemoryStore.get_user_by_email("admin@acme.example")
    token = TokenService.issue_token(user, InMemoryStore)
    {:ok, claims} = TokenService.verify_token(token)

    for key <- ~w[iss aud sub exp iat nbf jti tenant_role permissions acl_ver] do
      assert Map.has_key?(claims, key)
    end
  end

  test "expiry is fifteen minutes" do
    user = InMemoryStore.get_user_by_email("admin@acme.example")
    {:ok, claims} = user |> TokenService.issue_token(InMemoryStore) |> TokenService.verify_token()
    assert claims["exp"] - claims["iat"] == 900
  end

  test "permissions match store" do
    user = InMemoryStore.get_user_by_email("alice@acme.example")
    {:ok, claims} = user |> TokenService.issue_token(InMemoryStore) |> TokenService.verify_token()
    assert Enum.sort(claims["permissions"]) == InMemoryStore.get_effective_permissions(user.id)
  end
end
