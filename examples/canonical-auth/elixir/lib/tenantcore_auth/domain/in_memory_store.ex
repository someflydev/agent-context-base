defmodule TenantcoreAuth.Domain.InMemoryStore do
  use GenServer

  alias TenantcoreAuth.Domain.{Group, GroupPermission, Membership, Permission, Tenant, User, UserGroup}

  @canonical_permissions [
    "iam:user:read",
    "iam:user:create",
    "iam:user:update",
    "iam:user:delete",
    "iam:user:invite",
    "iam:group:read",
    "iam:group:create",
    "iam:group:update",
    "iam:group:delete",
    "iam:group:assign_permission",
    "iam:group:assign_user",
    "iam:tenant:read",
    "iam:tenant:create",
    "iam:tenant:update",
    "iam:permission:read",
    "billing:invoice:read",
    "billing:invoice:create",
    "billing:subscription:read",
    "billing:subscription:update",
    "reports:usage:read",
    "reports:usage:export",
    "reports:audit:read",
    "admin:tenant:create",
    "admin:tenant:suspend",
    "admin:audit:read"
  ]

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @impl true
  def init(_opts) do
    {:ok, load_fixtures(default_fixture_dir())}
  end

  def get_user_by_id(id), do: GenServer.call(__MODULE__, {:get_user_by_id, id})
  def get_user_by_email(email), do: GenServer.call(__MODULE__, {:get_user_by_email, email})
  def get_tenant_name(id), do: GenServer.call(__MODULE__, {:get_tenant_name, id})
  def get_groups_for_user(user_id, tenant_id), do: GenServer.call(__MODULE__, {:get_groups_for_user, user_id, tenant_id})
  def get_effective_permissions(user_id), do: GenServer.call(__MODULE__, {:get_effective_permissions, user_id})
  def verify_membership(user_id, tenant_id), do: GenServer.call(__MODULE__, {:verify_membership, user_id, tenant_id})
  def get_active_membership(user_id), do: GenServer.call(__MODULE__, {:get_active_membership, user_id})
  def list_users(tenant_id), do: GenServer.call(__MODULE__, {:list_users, tenant_id})
  def list_groups(tenant_id), do: GenServer.call(__MODULE__, {:list_groups, tenant_id})
  def list_permissions, do: GenServer.call(__MODULE__, :list_permissions)
  def list_tenants, do: GenServer.call(__MODULE__, :list_tenants)
  def get_group_by_id(id), do: GenServer.call(__MODULE__, {:get_group_by_id, id})

  def invite_user(tenant_id, email, display_name, group_slugs \\ []) do
    GenServer.call(__MODULE__, {:invite_user, tenant_id, email, display_name, group_slugs})
  end

  def create_group(tenant_id, slug, name, permission_names \\ []) do
    GenServer.call(__MODULE__, {:create_group, tenant_id, slug, name, permission_names})
  end

  def assign_permission_to_group(group_id, permission_name, tenant_id) do
    GenServer.call(__MODULE__, {:assign_permission_to_group, group_id, permission_name, tenant_id})
  end

  def assign_user_to_group(group_id, user_id, tenant_id) do
    GenServer.call(__MODULE__, {:assign_user_to_group, group_id, user_id, tenant_id})
  end

  def create_tenant(slug, name, first_admin_email) do
    GenServer.call(__MODULE__, {:create_tenant, slug, name, first_admin_email})
  end

  @impl true
  def handle_call({:get_user_by_id, id}, _from, state), do: {:reply, Map.get(state.users_by_id, id), state}
  def handle_call({:get_user_by_email, email}, _from, state), do: {:reply, Map.get(state.users_by_email, email), state}
  def handle_call({:get_tenant_name, id}, _from, state), do: {:reply, get_in(state.tenants_by_id, [id, Access.key(:name)]), state}
  def handle_call({:get_group_by_id, id}, _from, state), do: {:reply, Map.get(state.groups_by_id, id), state}

  def handle_call({:get_groups_for_user, user_id, tenant_id}, _from, state) do
    group_ids = state.user_groups |> Enum.filter(&(&1.user_id == user_id)) |> Enum.map(& &1.group_id) |> MapSet.new()
    groups =
      state.groups
      |> Enum.filter(&MapSet.member?(group_ids, &1.id))
      |> Enum.filter(&(&1.tenant_id == tenant_id))
    {:reply, groups, state}
  end

  def handle_call({:get_effective_permissions, user_id}, _from, state) do
    membership = Enum.find(state.memberships, &(&1.user_id == user_id and &1.is_active))

    permissions =
      case membership && membership.tenant_role do
        "tenant_admin" ->
          state.permissions |> Enum.map(& &1.name) |> Enum.sort()

        "super_admin" ->
          state.permissions |> Enum.map(& &1.name) |> Enum.filter(&String.starts_with?(&1, "admin:")) |> Enum.sort()

        _ ->
          group_ids = state.user_groups |> Enum.filter(&(&1.user_id == user_id)) |> Enum.map(& &1.group_id) |> MapSet.new()

          state.group_permissions
          |> Enum.filter(&MapSet.member?(group_ids, &1.group_id))
          |> Enum.map(&Map.get(state.permissions_by_id, &1.permission_id))
          |> Enum.reject(&is_nil/1)
          |> Enum.map(& &1.name)
          |> Enum.uniq()
          |> Enum.sort()
      end

    {:reply, permissions, state}
  end

  def handle_call({:verify_membership, user_id, tenant_id}, _from, state) do
    result = Enum.any?(state.memberships, &(&1.user_id == user_id and &1.tenant_id == tenant_id and &1.is_active))
    {:reply, result, state}
  end

  def handle_call({:get_active_membership, user_id}, _from, state) do
    {:reply, Enum.find(state.memberships, &(&1.user_id == user_id and &1.is_active)), state}
  end

  def handle_call({:list_users, tenant_id}, _from, state) do
    {:reply, state.users |> Enum.filter(&(&1.tenant_id == tenant_id)) |> Enum.sort_by(& &1.email), state}
  end

  def handle_call({:list_groups, tenant_id}, _from, state) do
    {:reply, state.groups |> Enum.filter(&(&1.tenant_id == tenant_id)) |> Enum.sort_by(& &1.slug), state}
  end

  def handle_call(:list_permissions, _from, state), do: {:reply, Enum.sort_by(state.permissions, & &1.name), state}
  def handle_call(:list_tenants, _from, state), do: {:reply, Enum.sort_by(state.tenants, & &1.slug), state}

  def handle_call({:invite_user, tenant_id, email, display_name, group_slugs}, _from, state) do
    user = %User{id: "u-#{unique_id()}", email: email, display_name: display_name, tenant_id: tenant_id, created_at: now_iso(), is_active: true, acl_ver: 1}
    membership = %Membership{id: "m-#{unique_id()}", user_id: user.id, tenant_id: tenant_id, tenant_role: "tenant_member", created_at: now_iso(), is_active: true}

    user_groups =
      group_slugs
      |> Enum.map(fn slug -> Enum.find(state.groups, &(&1.slug == slug and &1.tenant_id == tenant_id)) end)
      |> Enum.reject(&is_nil/1)
      |> Enum.map(fn group -> %UserGroup{id: "ug-#{unique_id()}", user_id: user.id, group_id: group.id, joined_at: now_iso()} end)

    new_state = rebuild_state(%{
      state
      | users: [user | state.users],
        memberships: [membership | state.memberships],
        user_groups: user_groups ++ state.user_groups
    })

    {:reply, user, new_state}
  end

  def handle_call({:create_group, tenant_id, slug, name, permission_names}, _from, state) do
    group = %Group{id: "g-#{unique_id()}", tenant_id: tenant_id, slug: slug, name: name, created_at: now_iso()}

    group_permissions =
      permission_names
      |> Enum.map(&Map.get(state.permissions_by_name, &1))
      |> Enum.reject(&is_nil/1)
      |> Enum.map(fn permission ->
        %GroupPermission{id: "gp-#{unique_id()}", group_id: group.id, permission_id: permission.id, granted_at: now_iso()}
      end)

    new_state = rebuild_state(%{state | groups: [group | state.groups], group_permissions: group_permissions ++ state.group_permissions})
    {:reply, group, new_state}
  end

  def handle_call({:assign_permission_to_group, group_id, permission_name, tenant_id}, _from, state) do
    group = Map.get(state.groups_by_id, group_id)
    permission = Map.get(state.permissions_by_name, permission_name)

    cond do
      is_nil(group) or is_nil(permission) or group.tenant_id != tenant_id ->
        {:reply, false, state}

      Enum.any?(state.group_permissions, &(&1.group_id == group_id and &1.permission_id == permission.id)) ->
        {:reply, true, state}

      true ->
        new_row = %GroupPermission{id: "gp-#{unique_id()}", group_id: group_id, permission_id: permission.id, granted_at: now_iso()}
        {:reply, true, rebuild_state(%{state | group_permissions: [new_row | state.group_permissions]})}
    end
  end

  def handle_call({:assign_user_to_group, group_id, user_id, tenant_id}, _from, state) do
    group = Map.get(state.groups_by_id, group_id)
    user = Map.get(state.users_by_id, user_id)

    cond do
      is_nil(group) or is_nil(user) or group.tenant_id != tenant_id or user.tenant_id != tenant_id ->
        {:reply, false, state}

      Enum.any?(state.user_groups, &(&1.group_id == group_id and &1.user_id == user_id)) ->
        {:reply, true, state}

      true ->
        row = %UserGroup{id: "ug-#{unique_id()}", user_id: user_id, group_id: group_id, joined_at: now_iso()}
        {:reply, true, rebuild_state(%{state | user_groups: [row | state.user_groups]})}
    end
  end

  def handle_call({:create_tenant, slug, name, first_admin_email}, _from, state) do
    tenant = %Tenant{id: "t-#{unique_id()}", slug: slug, name: name, created_at: now_iso(), is_active: true}
    admin = %User{id: "u-#{unique_id()}", email: first_admin_email, display_name: "#{name} Admin", tenant_id: tenant.id, created_at: now_iso(), is_active: true, acl_ver: 1}
    membership = %Membership{id: "m-#{unique_id()}", user_id: admin.id, tenant_id: tenant.id, tenant_role: "tenant_admin", created_at: now_iso(), is_active: true}

    new_state =
      rebuild_state(%{
        state
        | tenants: [tenant | state.tenants],
          users: [admin | state.users],
          memberships: [membership | state.memberships]
      })

    {:reply, tenant, new_state}
  end

  def default_fixture_dir do
    Path.expand("../../../../domain/fixtures", __DIR__)
  end

  defp load_fixtures(dir) do
    users = load_json(dir, "users.json", User)
    tenants = load_json(dir, "tenants.json", Tenant)
    groups = load_json(dir, "groups.json", Group)
    permissions = load_json(dir, "permissions.json", Permission)
    memberships = load_json(dir, "memberships.json", Membership)
    group_permissions = load_json(dir, "group_permissions.json", GroupPermission)
    user_groups = load_json(dir, "user_groups.json", UserGroup)

    permissions =
      Enum.reduce(@canonical_permissions, permissions, fn name, acc ->
        if Enum.any?(acc, &(&1.name == name)) do
          acc
        else
          [%Permission{id: "perm-#{String.replace(name, ":", "-")}", name: name, description: "Canonical seeded permission", created_at: "2025-01-01T00:00:00Z"} | acc]
        end
      end)

    rebuild_state(%{
      users: users,
      tenants: tenants,
      groups: groups,
      permissions: permissions,
      memberships: memberships,
      group_permissions: group_permissions,
      user_groups: user_groups
    })
  end

  defp load_json(dir, filename, struct_module) do
    dir
    |> Path.join(filename)
    |> File.read!()
    |> Jason.decode!()
    |> Enum.map(&struct(struct_module, atomize_keys(&1)))
  end

  defp atomize_keys(map) do
    Map.new(map, fn {key, value} -> {String.to_atom(key), value} end)
  end

  defp rebuild_state(state) do
    Map.merge(state, %{
      users_by_id: Map.new(state.users, &{&1.id, &1}),
      users_by_email: Map.new(state.users, &{&1.email, &1}),
      tenants_by_id: Map.new(state.tenants, &{&1.id, &1}),
      groups_by_id: Map.new(state.groups, &{&1.id, &1}),
      permissions_by_id: Map.new(state.permissions, &{&1.id, &1}),
      permissions_by_name: Map.new(state.permissions, &{&1.name, &1})
    })
  end

  defp unique_id, do: System.unique_integer([:positive]) |> Integer.to_string()
  defp now_iso, do: DateTime.utc_now() |> DateTime.truncate(:second) |> DateTime.to_iso8601()
end
