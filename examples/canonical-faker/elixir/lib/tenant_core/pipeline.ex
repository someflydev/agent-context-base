defmodule TenantCore.Pipeline do
  alias TenantCore.{Distributions, Pools}

  def generate(%TenantCore.Profile{} = profile) do
    :rand.seed(:exsss, {profile.seed, 0, 0})
    
    orgs = build_orgs(profile.num_orgs)
    users = build_users(profile.num_users)
    user_ids = Enum.map(users, & &1.id)

    {memberships, org_member_map} = build_memberships(orgs, user_ids)
    {projects, project_org_map} = build_projects(orgs, org_member_map)
    api_keys = build_api_keys(orgs, org_member_map)
    invitations = build_invitations(orgs, org_member_map)
    audit_events = build_audit_events(projects, org_member_map, project_org_map, memberships, api_keys, invitations)

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

  defp deterministic_timestamp(after_iso \\ "2020-01-01T00:00:00Z", max_offset_days \\ 365) do
    base = after_iso |> String.replace("Z", "") |> NaiveDateTime.from_iso8601!()
    offset = :rand.uniform(max_offset_days * 24 * 60 * 60)
    (NaiveDateTime.add(base, offset, :second) |> NaiveDateTime.to_iso8601()) <> "Z"
  end

  defp future_timestamp(after_iso \\ "2026-01-01T12:00:01Z") do
    base = after_iso |> String.replace("Z", "") |> NaiveDateTime.from_iso8601!()
    # Add at least 1 day, up to 30 days
    offset = :rand.uniform(30 * 24 * 60 * 60) + 86400
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
        members = Enum.take_random(user_ids, num_members)
        
        Enum.with_index(members)
        |> Enum.map(fn {uid, idx} ->
          role = if idx == 0, do: "owner", else: Distributions.weighted_role(nil)
          joined_at = deterministic_timestamp(org.created_at, 30)
          
          invited_by = if idx == 0, do: nil, else: Enum.at(members, 0)

          %TenantCore.Membership{
            id: deterministic_uuid(),
            org_id: org.id,
            user_id: uid,
            role: role,
            joined_at: joined_at,
            invited_by: invited_by
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

  defp build_audit_events(projects, org_member_map, _project_org_map, memberships, api_keys, invitations) do
    m_by_org = memberships |> Enum.group_by(& &1.org_id)
    ak_by_org = api_keys |> Enum.group_by(& &1.org_id)
    inv_by_org = invitations |> Enum.group_by(& &1.org_id)

    # Map user_id to their joined_at for temporal check
    joined_at_map = memberships 
      |> Enum.map(fn m -> {"#{m.org_id}:#{m.user_id}", m.joined_at} end)
      |> Map.new()

    Enum.flat_map(projects, fn project ->
      members = Map.get(org_member_map, project.org_id, [])
      org_api_keys = Map.get(ak_by_org, project.org_id, [])
      org_invitations = Map.get(inv_by_org, project.org_id, [])

      if members == [] do
        []
      else
        num_events = :rand.uniform(20) + 5
        Enum.map(1..num_events//1, fn _ ->
          type = Distributions.weighted_resource_type(nil)
          
          # Ensure we only pick a type if we have resources for it
          type = case type do
            "api_key" when org_api_keys == [] -> "project"
            "invitation" when org_invitations == [] -> "user"
            other -> other
          end

          res_id = case type do
            "project" -> project.id
            "user" -> Enum.random(members)
            "membership" -> (m_by_org[project.org_id] |> Enum.random()).id
            "api_key" -> (org_api_keys |> Enum.random()).id
            "invitation" -> (org_invitations |> Enum.random()).id
            _ -> project.id
          end

          user_id = Enum.random(members)
          joined_at = Map.get(joined_at_map, "#{project.org_id}:#{user_id}", project.created_at)

          %TenantCore.AuditEvent{
            id: deterministic_uuid(),
            org_id: project.org_id,
            user_id: user_id,
            project_id: project.id,
            action: Distributions.weighted_action(nil),
            resource_type: type,
            resource_id: res_id,
            ts: deterministic_timestamp(joined_at, 10)
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
              expires_at: future_timestamp(),
              accepted_at: nil
            }
          end)
        end
      end
    end)
  end
end
