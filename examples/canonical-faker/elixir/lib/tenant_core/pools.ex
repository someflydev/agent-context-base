defmodule TenantCore.Pools do
  def build_org_member_map(memberships) do
    Enum.reduce(memberships, %{}, fn m, acc ->
      Map.update(acc, m.org_id, [m.user_id], &[m.user_id | &1])
    end)
  end

  def build_project_org_map(projects) do
    Enum.reduce(projects, %{}, fn p, acc ->
      Map.put(acc, p.id, p.org_id)
    end)
  end
end
