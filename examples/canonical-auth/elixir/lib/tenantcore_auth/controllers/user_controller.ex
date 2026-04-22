defmodule TenantcoreAuth.UserController do
  use TenantcoreAuth, :controller

  alias TenantcoreAuth.Domain.InMemoryStore

  plug TenantcoreAuth.Auth.RbacPlug, "iam:user:read" when action in [:index, :show]
  plug TenantcoreAuth.Auth.RbacPlug, "iam:user:invite" when action in [:create]
  plug TenantcoreAuth.Auth.RbacPlug, "iam:user:update" when action in [:update]

  def index(%Plug.Conn{assigns: %{auth: auth}} = conn, _params) do
    users =
      InMemoryStore.list_users(auth.tenant_id)
      |> Enum.map(&serialize_user/1)

    json(conn, %{users: users})
  end

  def show(%Plug.Conn{assigns: %{auth: auth}} = conn, %{"id" => id}) do
    case InMemoryStore.get_user_by_id(id) do
      %{tenant_id: tenant_id} = user when tenant_id == auth.tenant_id ->
        json(conn, %{user: serialize_user(user)})

      _ ->
        conn |> put_status(:forbidden) |> json(%{error: "Forbidden"})
    end
  end

  def create(%Plug.Conn{assigns: %{auth: auth}} = conn, %{"email" => email, "display_name" => display_name} = params) do
    user = InMemoryStore.invite_user(auth.tenant_id, email, display_name, Map.get(params, "group_slugs", []))
    conn |> put_status(:created) |> json(%{user: serialize_user(user)})
  end

  def update(%Plug.Conn{assigns: %{auth: auth}} = conn, %{"id" => id, "display_name" => display_name}) do
    case InMemoryStore.get_user_by_id(id) do
      %{tenant_id: tenant_id} = user when tenant_id == auth.tenant_id ->
        user = %{user | display_name: display_name}
        json(conn, %{user: serialize_user(user)})

      _ ->
        conn |> put_status(:forbidden) |> json(%{error: "Forbidden"})
    end
  end

  defp serialize_user(user) do
    %{id: user.id, email: user.email, display_name: user.display_name, tenant_id: user.tenant_id, acl_ver: user.acl_ver}
  end
end
