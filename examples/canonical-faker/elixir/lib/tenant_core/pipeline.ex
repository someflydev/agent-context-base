defmodule TenantCore.Pipeline do
  alias TenantCore.{Distributions, Pools}

  def generate(%TenantCore.Profile{} = profile) do
    :rand.seed(:exsss, {profile.seed, 0, 0})
    
    orgs = build_orgs(profile.num_orgs)
    users = build_users(profile.num_users)
    user_ids = Enum.map(users, & &1.id)

    {memberships, org_member_map} = build_memberships(orgs, user_ids)
    {projects, project_org_map} = build_projects(orgs, org_member_map)
    audit_events = build_audit_events(projects, org_member_map, project_org_map)
    api_keys = build_api_keys(orgs, org_member_map)
    invitations = build_invitations(orgs, org_member_map)

    dataset = %{
      organizations: orgs,
      users: users,
      memberships: memberships,
      projects: projects,
      audit_events: audit_events,
      api_keys: api_keys,
      invitations: invitations
    }

    report = TenantCore.Validate.check(dataset)
    unless report.ok, do: raise("Validation failed: #{inspect(report.violations)}")
    Map.put(dataset, :report, report)
  end

  defp deterministic_uuid do
    bytes = for _ <- 1..16, into: <<>>, do: <<:rand.uniform(256) - 1>>
    <<u0::48, _::4, u1::12, _::2, u2::62>> = bytes
    <<u0::48, 4::4, u1::12, 2::2, u2::62>>
    |> Base.encode16(case: :lower)
    |> (fn <<a::8-bytes, b::4-bytes, c::4-bytes, d::4-bytes, e::12-bytes>> -> "#{a}-#{b}-#{c}-#{d}-#{e}" end).()
  end

  defp deterministic_timestamp do
    base = ~N[2020-01-01 00:00:00]
    offset = :rand.uniform(365 * 3 * 24 * 60 * 60)
    (NaiveDateTime.add(base, offset, :second) |> NaiveDateTime.to_iso8601()) <> "Z"
  end

  defp deterministic_string(len) do
    bytes = for _ <- 1..len, into: <<>>, do: <<:rand.uniform(256) - 1>>
    Base.encode16(bytes, case: :lower) |> String.slice(0, len)
  end

  defp build_orgs(count) do
    Enum.map(1..count, fn _ ->
      %TenantCore.Organization{
        id: deterministic_uuid(),
        name: Faker.Company.name(),
        slug: Faker.Internet.slug(),
        plan: Distributions.weighted_plan(nil),
        region: Distributions.weighted_region(nil),
        created_at: deterministic_timestamp(),
        owner_email: Faker.Internet.email()
      }
    end)
  end

  defp build_users(count) do
    Enum.map(1..count, fn _ ->
      locale = Distributions.weighted_locale(nil)
      %TenantCore.User{
        id: deterministic_uuid(),
        email: Faker.Internet.email(),
        full_name: Faker.Person.name(),
        locale: locale,
        timezone: Distributions.timezone_for_locale(locale),
        created_at: deterministic_timestamp()
      }
    end)
  end

  defp build_memberships(orgs, user_ids) do
    memberships =
      Enum.flat_map(orgs, fn org ->
        num_members = :rand.uniform(10) + 2
        # Enum.take_random is not purely driven by :rand for small lists? Wait, it uses :rand.
        # But to be safe we can use deterministic shuffle if take_random fails.
        # In Elixir, Enum.take_random uses :rand.
        members = Enum.take_random(user_ids, num_members)
        
        Enum.with_index(members)
        |> Enum.map(fn {uid, idx} ->
          role = if idx == 0, do: "owner", else: Distributions.weighted_role(nil)
          %TenantCore.Membership{
            id: deterministic_uuid(),
            org_id: org.id,
            user_id: uid,
            role: role,
            joined_at: org.created_at,
            invited_by: nil
          }
        end)
      end)
    {memberships, Pools.build_org_member_map(memberships)}
  end

  defp build_projects(orgs, org_member_map) do
    projects =
      Enum.flat_map(orgs, fn org ->
        members = Map.get(org_member_map, org.id, [])
        if members == [] do
          []
        else
          num_projects = :rand.uniform(5)
          Enum.map(1..num_projects//1, fn _ ->
            %TenantCore.Project{
              id: deterministic_uuid(),
              org_id: org.id,
              name: Faker.Commerce.product_name(),
              status: Distributions.weighted_project_status(nil),
              created_by: Enum.random(members),
              created_at: org.created_at
            }
          end)
        end
      end)
    {projects, Pools.build_project_org_map(projects)}
  end

  defp build_audit_events(projects, org_member_map, _project_org_map) do
    Enum.flat_map(projects, fn project ->
      members = Map.get(org_member_map, project.org_id, [])
      if members == [] do
        []
      else
        num_events = :rand.uniform(5)
        Enum.map(1..num_events//1, fn _ ->
          %TenantCore.AuditEvent{
            id: deterministic_uuid(),
            org_id: project.org_id,
            user_id: Enum.random(members),
            project_id: project.id,
            action: Distributions.weighted_action(nil),
            resource_type: Distributions.weighted_resource_type(nil),
            resource_id: deterministic_uuid(),
            ts: project.created_at
          }
        end)
      end
    end)
  end

  defp build_api_keys(orgs, org_member_map) do
    Enum.flat_map(orgs, fn org ->
      members = Map.get(org_member_map, org.id, [])
      if members == [] do
        []
      else
        num_keys = :rand.uniform(3) - 1
        if num_keys <= 0 do
          []
        else
          Enum.map(1..num_keys, fn _ ->
            %TenantCore.ApiKey{
              id: deterministic_uuid(),
              org_id: org.id,
              created_by: Enum.random(members),
              name: Faker.Lorem.word(),
              key_prefix: "tc_" <> deterministic_string(8),
              created_at: org.created_at,
              last_used_at: org.created_at
            }
          end)
        end
      end
    end)
  end

  defp build_invitations(orgs, org_member_map) do
    Enum.flat_map(orgs, fn org ->
      members = Map.get(org_member_map, org.id, [])
      if members == [] do
        []
      else
        num_invites = :rand.uniform(3) - 1
        if num_invites <= 0 do
          []
        else
          Enum.map(1..num_invites, fn _ ->
            %TenantCore.Invitation{
              id: deterministic_uuid(),
              org_id: org.id,
              invited_email: Faker.Internet.email() <> ".inv",
              role: Distributions.weighted_role(nil),
              invited_by: Enum.random(members),
              expires_at: deterministic_timestamp(),
              accepted_at: nil
            }
          end)
        end
      end
    end)
  end
end
