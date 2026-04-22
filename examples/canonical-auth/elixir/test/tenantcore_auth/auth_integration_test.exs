defmodule TenantcoreAuth.AuthIntegrationTest do
  use TenantcoreAuth.ConnCase, async: true

  alias TenantcoreAuth.Auth.TokenService
  alias TenantcoreAuth.Domain.InMemoryStore

  setup do
    System.put_env("TENANTCORE_TEST_SECRET", "tenantcore-test-secret")
    :ok
  end

  defp with_auth(conn, email) do
    user = InMemoryStore.get_user_by_email(email)
    put_req_header(conn, "authorization", "Bearer " <> TokenService.issue_token(user, InMemoryStore))
  end

  test "token_issue_success", %{conn: conn} do
    body = conn |> post("/auth/token", %{email: "admin@acme.example", password: "password"}) |> json_response(200)
    assert Map.has_key?(body, "access_token")
  end

  test "token_invalid_credentials", %{conn: conn} do
    assert conn |> post("/auth/token", %{email: "admin@acme.example", password: "wrong"}) |> response(401)
  end

  test "token_expired_rejection", %{conn: conn} do
    user = InMemoryStore.get_user_by_email("admin@acme.example")
    now = DateTime.utc_now() |> DateTime.to_unix()
    expired =
      TenantcoreAuth.Auth.TokenService.sign_claims!(%{
        "sub" => user.id,
        "iss" => "tenantcore-auth",
        "aud" => "tenantcore-api",
        "exp" => now - 1,
        "iat" => now - 2,
        "nbf" => now - 2,
        "jti" => "expired",
        "tenant_id" => user.tenant_id,
        "tenant_role" => "tenant_admin",
        "groups" => ["iam-admins"],
        "permissions" => InMemoryStore.get_effective_permissions(user.id),
        "acl_ver" => user.acl_ver
      })
    assert conn |> put_req_header("authorization", "Bearer " <> expired) |> get("/me") |> response(401)
  end

  test "token_stale_acl_ver", %{conn: conn} do
    user = InMemoryStore.get_user_by_email("admin@acme.example")
    now = DateTime.utc_now() |> DateTime.to_unix()
    stale =
      TenantcoreAuth.Auth.TokenService.sign_claims!(%{
        "sub" => user.id,
        "iss" => "tenantcore-auth",
        "aud" => "tenantcore-api",
        "exp" => now + 60,
        "iat" => now,
        "nbf" => now,
        "jti" => "stale",
        "tenant_id" => user.tenant_id,
        "tenant_role" => "tenant_admin",
        "groups" => ["iam-admins"],
        "permissions" => InMemoryStore.get_effective_permissions(user.id),
        "acl_ver" => user.acl_ver - 1
      })
    assert conn |> put_req_header("authorization", "Bearer " <> stale) |> get("/me") |> response(401)
  end

  test "get_me_success", %{conn: conn} do
    assert conn |> with_auth("admin@acme.example") |> get("/me") |> response(200)
  end

  test "get_me_unauthorized", %{conn: conn} do
    assert conn |> get("/me") |> response(401)
  end

  test "rbac_permission_granted", %{conn: conn} do
    assert conn |> with_auth("admin@acme.example") |> get("/users") |> response(200)
  end

  test "rbac_permission_denied", %{conn: conn} do
    assert conn |> with_auth("bob@acme.example") |> post("/groups", %{slug: "extra", name: "Extra"}) |> response(403)
  end

  test "cross_tenant_denial", %{conn: conn} do
    target = InMemoryStore.get_user_by_email("admin@globex.example")
    assert conn |> with_auth("admin@acme.example") |> get("/users/#{target.id}") |> response(403)
  end

  test "super_admin_access", %{conn: conn} do
    assert conn |> with_auth("superadmin@tenantcore.dev") |> get("/admin/tenants") |> response(200)
  end

  test "super_admin_tenant_scoped_denial", %{conn: conn} do
    assert conn |> with_auth("superadmin@tenantcore.dev") |> get("/users") |> response(403)
  end

  test "me_allowed_routes_match_permissions", %{conn: conn} do
    body = conn |> with_auth("admin@acme.example") |> get("/me") |> json_response(200)
    paths = Enum.map(body["allowed_routes"], & &1["path"])
    assert "/users" in paths
    refute "/admin/tenants" in paths
  end
end
