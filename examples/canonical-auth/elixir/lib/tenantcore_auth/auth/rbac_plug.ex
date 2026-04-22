defmodule TenantcoreAuth.Auth.RbacPlug do
  import Plug.Conn

  alias TenantcoreAuth.Auth.AuthContext

  def init(permission), do: permission

  def call(conn, permission) do
    case conn.assigns[:auth] do
      nil ->
        conn |> put_resp_content_type("application/json") |> send_resp(401, Jason.encode!(%{error: "Unauthorized"})) |> halt()

      auth ->
        if AuthContext.has_permission?(auth, permission) do
          conn
        else
          conn |> put_resp_content_type("application/json") |> send_resp(403, Jason.encode!(%{error: "Forbidden"})) |> halt()
        end
    end
  end
end
