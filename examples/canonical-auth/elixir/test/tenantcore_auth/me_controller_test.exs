defmodule TenantcoreAuth.MeControllerTest do
  use TenantcoreAuth.ConnCase, async: true

  alias TenantcoreAuth.Auth.TokenService
  alias TenantcoreAuth.Domain.InMemoryStore

  setup do
    System.put_env("TENANTCORE_TEST_SECRET", "tenantcore-test-secret")
    :ok
  end

  defp auth_header(email) do
    user = InMemoryStore.get_user_by_email(email)
    [{"authorization", "Bearer " <> TokenService.issue_token(user, InMemoryStore)}]
  end

  test "/me returns the required fields", %{conn: conn} do
    conn = Enum.reduce(auth_header("admin@acme.example"), conn, fn {key, value}, acc -> put_req_header(acc, key, value) end)
    conn = get(conn, "/me")
    body = json_response(conn, 200)

    for key <- ~w[sub email display_name tenant_id tenant_name tenant_role groups permissions acl_ver allowed_routes guide_sections issued_at expires_at] do
      assert Map.has_key?(body, key)
    end
  end

  test "/me filters allowed_routes", %{conn: conn} do
    conn = Enum.reduce(auth_header("bob@acme.example"), conn, fn {key, value}, acc -> put_req_header(acc, key, value) end)
    body = conn |> get("/me") |> json_response(200)
    paths = Enum.map(body["allowed_routes"], & &1["path"])
    assert "/users" in paths
    refute "/admin/tenants" in paths
  end

  test "super_admin /me shape", %{conn: conn} do
    conn = Enum.reduce(auth_header("superadmin@tenantcore.dev"), conn, fn {key, value}, acc -> put_req_header(acc, key, value) end)
    body = conn |> get("/me") |> json_response(200)
    assert body["tenant_role"] == "super_admin"
    assert body["tenant_id"] == nil
    assert body["groups"] == []
  end
end
