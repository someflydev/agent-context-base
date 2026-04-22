defmodule TenantcoreAuth.Auth.JwtPlug do
  import Plug.Conn

  alias TenantcoreAuth.Auth.{AuthContext, TokenService}
  alias TenantcoreAuth.Domain.InMemoryStore

  def init(opts), do: opts

  def call(conn, _opts) do
    with {:ok, token} <- extract_token(conn),
         {:ok, claims} <- TokenService.verify_token(token),
         %{} = user <- InMemoryStore.get_user_by_id(claim(claims, "sub")),
         :ok <- verify_acl_ver(claims, user),
         :ok <- verify_membership(claims, user) do
      assign(conn, :auth, build_auth_context(claims, user))
    else
      {:error, :missing_token} ->
        conn

      nil ->
        unauthorized(conn)

      {:error, :forbidden} ->
        forbidden(conn)

      {:error, _reason} ->
        unauthorized(conn)
    end
  end

  defp extract_token(conn) do
    case get_req_header(conn, "authorization") do
      ["Bearer " <> token] -> {:ok, String.trim(token)}
      _ -> {:error, :missing_token}
    end
  end

  defp verify_acl_ver(claims, user) do
    if claim(claims, "acl_ver") == user.acl_ver, do: :ok, else: {:error, :stale_acl}
  end

  defp verify_membership(claims, _user) do
    tenant_role = claim(claims, "tenant_role")
    tenant_id = claim(claims, "tenant_id")
    sub = claim(claims, "sub")

    cond do
      tenant_role == "super_admin" -> :ok
      tenant_id in [nil, "null"] -> :ok
      InMemoryStore.verify_membership(sub, tenant_id) -> :ok
      true -> {:error, :forbidden}
    end
  end

  defp build_auth_context(claims, user) do
    tenant_id = normalize_nullable(claim(claims, "tenant_id"))

    %AuthContext{
      sub: claim(claims, "sub"),
      email: user.email,
      tenant_id: tenant_id,
      tenant_role: claim(claims, "tenant_role"),
      groups: claim(claims, "groups") || [],
      permissions: claim(claims, "permissions") || [],
      acl_ver: claim(claims, "acl_ver"),
      issued_at: DateTime.from_unix!(claim(claims, "iat")),
      expires_at: DateTime.from_unix!(claim(claims, "exp"))
    }
  end

  defp claim(claims, key) do
    Map.get(claims, key) || Map.get(claims, String.to_atom(key))
  end

  defp normalize_nullable(value) when value in [nil, "null", :null], do: nil
  defp normalize_nullable(~c"null"), do: nil
  defp normalize_nullable(value), do: value

  defp unauthorized(conn) do
    conn |> put_resp_content_type("application/json") |> send_resp(401, Jason.encode!(%{error: "Unauthorized"})) |> halt()
  end

  defp forbidden(conn) do
    conn |> put_resp_content_type("application/json") |> send_resp(403, Jason.encode!(%{error: "Forbidden"})) |> halt()
  end
end
