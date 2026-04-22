defmodule TenantcoreAuth.AuthController do
  use TenantcoreAuth, :controller

  alias TenantcoreAuth.Auth.TokenService
  alias TenantcoreAuth.Domain.InMemoryStore

  def token(conn, %{"email" => email, "password" => "password"}) do
    case InMemoryStore.get_user_by_email(email) do
      nil -> conn |> put_status(:unauthorized) |> json(%{error: "Unauthorized"})
      user -> json(conn, %{access_token: TokenService.issue_token(user, InMemoryStore), token_type: "Bearer"})
    end
  end

  def token(conn, _params) do
    conn |> put_status(:unauthorized) |> json(%{error: "Unauthorized"})
  end
end
