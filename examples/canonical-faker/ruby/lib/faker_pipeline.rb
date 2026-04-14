require 'faker'
require 'securerandom'
require 'date'
require_relative 'domain'
require_relative 'profiles'
require_relative 'distributions'
require_relative 'pools'

class FakerPipeline
  # Set Faker::Config.random once at pipeline startup and do not reset it mid-run.
  def self.generate(profile)
    Faker::Config.random = Random.new(profile.seed)
    rng = Random.new(profile.seed)

    dataset = {
      organizations: [],
      users: [],
      memberships: [],
      projects: [],
      audit_events: [],
      api_keys: [],
      invitations: []
    }

    org_member_map = {}
    users_by_id = {}

    seen_slugs = {}
    seen_org_emails = {}
    seen_user_emails = {}

    # 1. Organizations
    profile.num_orgs.times do
      name = Faker::Company.name
      slug = name.downcase.gsub(/[^a-z0-9]/, '-').gsub(/-+/, '-').chomp('-')
      slug = "tenantcore" if slug.empty?
      
      base_slug = slug
      suffix = 1
      while seen_slugs.key?(slug)
        suffix += 1
        slug = "#{base_slug}-#{suffix}"
      end
      seen_slugs[slug] = true

      email = Faker::Internet.unique.email
      while seen_org_emails.key?(email)
        email = Faker::Internet.unique.email
      end
      seen_org_emails[email] = true

      created_at = Faker::Time.between(from: Time.now - (3 * 365 * 24 * 60 * 60), to: Time.now).utc

      org = Organization.new(
        id: SecureRandom.uuid,
        name: name,
        slug: slug,
        plan: Distributions.weighted_choice(Distributions::PLAN_WEIGHTS, rng),
        region: Distributions.weighted_choice(Distributions::REGION_WEIGHTS, rng),
        created_at: created_at.iso8601,
        owner_email: email
      )
      dataset[:organizations] << org
      org_member_map[org.id] = []
    end

    # 2. Users
    profile.num_users.times do
      email = Faker::Internet.unique.email
      while seen_user_emails.key?(email)
        email = Faker::Internet.unique.email
      end
      seen_user_emails[email] = true

      locale = Distributions.weighted_choice(Distributions::LOCALE_WEIGHTS, rng)
      timezone = Distributions::TIMEZONE_BY_LOCALE[locale]
      created_at = Faker::Time.between(from: Time.now - (3 * 365 * 24 * 60 * 60), to: Time.now).utc

      user = User.new(
        id: SecureRandom.uuid,
        email: email,
        full_name: Faker::Name.name,
        locale: locale,
        timezone: timezone,
        created_at: created_at.iso8601
      )
      dataset[:users] << user
      users_by_id[user.id] = user
    end

    # 3. Memberships
    user_ids = dataset[:users].map(&:id)
    dataset[:organizations].each do |org|
      org_created = Time.parse(org.created_at)
      count = Distributions.bounded_count(rng, 3, [50, user_ids.size].min, 6)
      count = [count, user_ids.size].min
      member_ids = user_ids.sample(count, random: rng)
      
      org_member_map[org.id] = member_ids

      member_ids.each_with_index do |user_id, index|
        role = index == 0 ? "owner" : Distributions.weighted_choice(Distributions::ROLE_WEIGHTS, rng)
        joined_at = org_created + rng.rand(0..365 * 24 * 60 * 60)
        
        invited_by = nil
        if role != "owner" && index > 0
          invited_by = member_ids[0...index].sample(random: rng)
        end

        dataset[:memberships] << Membership.new(
          id: SecureRandom.uuid,
          org_id: org.id,
          user_id: user_id,
          role: role,
          joined_at: joined_at.utc.iso8601,
          invited_by: invited_by
        )
      end
    end

    # 4. Projects
    dataset[:organizations].each do |org|
      org_created = Time.parse(org.created_at)
      count = Distributions.bounded_count(rng, 1, 20, 3.5)
      count.times do
        created_by = org_member_map[org.id].sample(random: rng)
        created_at = org_created + rng.rand(0..540 * 24 * 60 * 60)
        project = Project.new(
          id: SecureRandom.uuid,
          org_id: org.id,
          name: Faker::Commerce.product_name,
          status: Distributions.weighted_choice(Distributions::PROJECT_STATUS_WEIGHTS, rng),
          created_by: created_by,
          created_at: created_at.utc.iso8601
        )
        dataset[:projects] << project
      end
    end

    # 5. Audit Events
    membership_lookup = {}
    dataset[:memberships].each { |m| membership_lookup[[m.org_id, m.user_id]] = m }

    dataset[:projects].each do |project|
      org_id = project.org_id
      member_ids = org_member_map[org_id]
      project_created = Time.parse(project.created_at)
      
      count = case project.status
              when "active" then Distributions.bounded_count(rng, 8, 30, 14)
              when "archived" then Distributions.bounded_count(rng, 4, 18, 8)
              else Distributions.bounded_count(rng, 2, 10, 4)
              end
              
      count.times do
        user_id = member_ids.sample(random: rng)
        membership = membership_lookup[[org_id, user_id]]
        membership_joined_at = Time.parse(membership.joined_at)
        
        event_floor = [project_created, membership_joined_at].max
        ts = project_created + rng.rand(0..365 * 24 * 60 * 60)
        ts = event_floor + rng.rand(0..3600) if ts < event_floor

        resource_candidates = [
          ["project", project.id],
          ["user", user_id]
        ]
        
        resource_type, resource_id = resource_candidates.sample(random: rng)

        dataset[:audit_events] << AuditEvent.new(
          id: SecureRandom.uuid,
          org_id: org_id,
          user_id: user_id,
          project_id: project.id,
          action: Distributions.weighted_choice(Distributions::AUDIT_ACTION_WEIGHTS, rng),
          resource_type: resource_type,
          resource_id: resource_id,
          ts: ts.utc.iso8601
        )
      end
    end

    # 6. Api Keys
    seen_prefixes = {}
    alphabet = ('a'..'z').to_a + ('0'..'9').to_a
    dataset[:organizations].each do |org|
      org_created = Time.parse(org.created_at)
      count = Distributions.bounded_count(rng, 0, 10, 2)
      count.times do
        suffix = Array.new(8) { alphabet.sample(random: rng) }.join
        key_prefix = "tc_#{suffix}"
        while seen_prefixes.key?(key_prefix)
          suffix = Array.new(8) { alphabet.sample(random: rng) }.join
          key_prefix = "tc_#{suffix}"
        end
        seen_prefixes[key_prefix] = true

        created_at = org_created + rng.rand(0..540 * 24 * 60 * 60)
        last_used_at = nil
        if rng.rand > 0.30
          last_used_at = (created_at + rng.rand(0..180 * 24 * 60 * 60)).utc.iso8601
        end

        dataset[:api_keys] << ApiKey.new(
          id: SecureRandom.uuid,
          org_id: org.id,
          created_by: org_member_map[org.id].sample(random: rng),
          name: Faker::Company.catch_phrase,
          key_prefix: key_prefix,
          created_at: created_at.utc.iso8601,
          last_used_at: last_used_at
        )
      end
    end

    # 7. Invitations
    dataset[:organizations].each do |org|
      member_emails = org_member_map[org.id].map { |uid| users_by_id[uid].email.downcase }
      count = Distributions.bounded_count(rng, 0, 5, 1.5)
      count.times do
        invited_email = Faker::Internet.unique.email
        while member_emails.include?(invited_email.downcase)
          invited_email = Faker::Internet.unique.email
        end

        accepted_at = nil
        if rng.rand < 0.40
          accepted_at = (Time.now - rng.rand(0..180 * 24 * 60 * 60)).utc.iso8601
        end

        dataset[:invitations] << Invitation.new(
          id: SecureRandom.uuid,
          org_id: org.id,
          invited_email: invited_email,
          role: Distributions.weighted_choice(Distributions::INVITATION_ROLE_WEIGHTS, rng),
          invited_by: org_member_map[org.id].sample(random: rng),
          expires_at: (Time.now + rng.rand(1..30 * 24 * 60 * 60)).utc.iso8601,
          accepted_at: accepted_at
        )
      end
    end

    dataset
  end
end