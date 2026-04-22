defmodule TenantcoreAuth.GroupController do
  use TenantcoreAuth, :controller

  alias TenantcoreAuth.Domain.InMemoryStore

  plug TenantcoreAuth.Auth.RbacPlug, "iam:group:read" when action in [:index]
  plug TenantcoreAuth.Auth.RbacPlug, "iam:group:create" when action in [:create]
  plug TenantcoreAuth.Auth.RbacPlug, "iam:group:assign_permission" when action in [:assign_permission]
  plug TenantcoreAuth.Auth.RbacPlug, "iam:group:assign_user" when action in [:assign_user]

  def index(%Plug.Conn{assigns: %{auth: auth}} = conn, _params) do
    groups =
      InMemoryStore.list_groups(auth.tenant_id)
      |> Enum.map(fn group -> %{id: group.id, tenant_id: group.tenant_id, slug: group.slug, name: group.name} end)

    json(conn, %{groups: groups})
  end

  def create(%Plug.Conn{assigns: %{auth: auth}} = conn, %{"slug" => slug, "name" => name} = params) do
    permission_names = Map.get(params, "permission_names", [])
    known_permissions = InMemoryStore.list_permissions() |> Enum.map(& &1.name) |> MapSet.new()
    unknown_permissions = Enum.reject(permission_names, &MapSet.member?(known_permissions, &1))

    if unknown_permissions == [] do
      group = InMemoryStore.create_group(auth.tenant_id, slug, name, permission_names)
      conn |> put_status(:created) |> json(%{group: %{id: group.id, tenant_id: group.tenant_id, slug: group.slug, name: group.name}})
    else
      conn |> put_status(:bad_request) |> json(%{error: "Unknown permissions", names: unknown_permissions})
    end
  end

  def assign_permission(%Plug.Conn{assigns: %{auth: auth}} = conn, %{"id" => id, "permission" => permission}) do
    if InMemoryStore.assign_permission_to_group(id, permission, auth.tenant_id) do
      conn |> put_status(:created) |> json(%{status: "assigned"})
    else
      conn |> put_status(:forbidden) |> json(%{error: "Forbidden"})
    end
  end

  def assign_user(%Plug.Conn{assigns: %{auth: auth}} = conn, %{"id" => id, "user_id" => user_id}) do
    if InMemoryStore.assign_user_to_group(id, user_id, auth.tenant_id) do
      conn |> put_status(:created) |> json(%{status: "assigned"})
    else
      conn |> put_status(:forbidden) |> json(%{error: "Forbidden"})
    end
  end
end
