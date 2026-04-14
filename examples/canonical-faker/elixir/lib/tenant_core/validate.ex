defmodule TenantCore.Validate do
  defmodule Report do
    defstruct ok: true, violations: [], counts: %{}, seed: 0, profile_name: ""
  end

  def check(dataset) do
    violations = []
      |> check_rule_a(dataset)
      |> check_rule_b(dataset)
      |> check_rule_c(dataset)
      |> check_rule_d(dataset)
      |> check_rule_e(dataset)
      |> check_rule_f(dataset)
      |> check_rule_g(dataset)
      |> check_rule_h(dataset)
      |> check_rule_i(dataset)

    %Report{
      ok: Enum.empty?(violations),
      violations: violations,
      counts: %{
        organizations: length(dataset.organizations),
        users: length(dataset.users),
        memberships: length(dataset.memberships),
        projects: length(dataset.projects),
        audit_events: length(dataset.audit_events),
        api_keys: length(dataset.api_keys),
        invitations: length(dataset.invitations)
      }
    }
  end

  defp check_rule_a(violations, dataset) do
    orgs = Enum.into(dataset.organizations, %{}, &{&1.id, &1})
    Enum.reduce(dataset.memberships, violations, fn m, acc ->
      org = orgs[m.org_id]
      if org && m.joined_at < org.created_at do
        ["Rule A violation: membership #{m.id}" | acc]
      else
        acc
      end
    end)
  end

  defp check_rule_b(violations, dataset) do
    orgs = Enum.into(dataset.organizations, %{}, &{&1.id, &1})
    Enum.reduce(dataset.projects, violations, fn p, acc ->
      org = orgs[p.org_id]
      if org && p.created_at < org.created_at do
        ["Rule B violation: project #{p.id}" | acc]
      else
        acc
      end
    end)
  end

  defp check_rule_c(violations, dataset) do
    members_by_org = build_members_by_org(dataset.memberships)
    Enum.reduce(dataset.projects, violations, fn p, acc ->
      if p.created_by in Map.get(members_by_org, p.org_id, []) do
        acc
      else
        ["Rule C violation: project #{p.id}" | acc]
      end
    end)
  end

  defp check_rule_d(violations, dataset) do
    members_by_org = build_members_by_org(dataset.memberships)
    Enum.reduce(dataset.audit_events, violations, fn e, acc ->
      if e.user_id in Map.get(members_by_org, e.org_id, []) do
        acc
      else
        ["Rule D violation: audit_event #{e.id}" | acc]
      end
    end)
  end

  defp check_rule_e(violations, dataset) do
    projects = Enum.into(dataset.projects, %{}, &{&1.id, &1})
    Enum.reduce(dataset.audit_events, violations, fn e, acc ->
      proj = projects[e.project_id]
      if proj && proj.org_id == e.org_id do
        acc
      else
        ["Rule E violation: audit_event #{e.id}" | acc]
      end
    end)
  end

  defp check_rule_f(violations, dataset) do
    projects = Enum.into(dataset.projects, %{}, &{&1.id, &1})
    Enum.reduce(dataset.audit_events, violations, fn e, acc ->
      proj = projects[e.project_id]
      if proj && e.ts < proj.created_at do
        ["Rule F violation: audit_event #{e.id}" | acc]
      else
        acc
      end
    end)
  end

  defp check_rule_g(violations, dataset) do
    members_by_org = build_members_by_org(dataset.memberships)
    Enum.reduce(dataset.api_keys, violations, fn k, acc ->
      if k.created_by in Map.get(members_by_org, k.org_id, []) do
        acc
      else
        ["Rule G violation: api_key #{k.id}" | acc]
      end
    end)
  end

  defp check_rule_h(violations, dataset) do
    members_by_org = build_members_by_org(dataset.memberships)
    Enum.reduce(dataset.invitations, violations, fn i, acc ->
      if i.invited_by in Map.get(members_by_org, i.org_id, []) do
        acc
      else
        ["Rule H violation: invitation #{i.id}" | acc]
      end
    end)
  end

  defp check_rule_i(violations, dataset) do
    member_emails_by_org = Enum.reduce(dataset.memberships, %{}, fn m, acc ->
      user = Enum.find(dataset.users, &(&1.id == m.user_id))
      if user do
        Map.update(acc, m.org_id, [user.email], &[user.email | &1])
      else
        acc
      end
    end)
    Enum.reduce(dataset.invitations, violations, fn i, acc ->
      if i.invited_email in Map.get(member_emails_by_org, i.org_id, []) do
        ["Rule I violation: invitation #{i.id}" | acc]
      else
        acc
      end
    end)
  end

  defp build_members_by_org(memberships) do
    Enum.reduce(memberships, %{}, fn m, acc ->
      Map.update(acc, m.org_id, [m.user_id], &[m.user_id | &1])
    end)
  end
end
