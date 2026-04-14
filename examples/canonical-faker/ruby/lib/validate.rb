require 'date'

ValidationReport = Struct.new(:ok, :violations, :counts, :seed, :profile_name, keyword_init: true)

class Validate
  def self.check(dataset)
    violations = []
    counts = {}
    
    entities = [:organizations, :users, :memberships, :projects, :audit_events, :api_keys, :invitations]
    
    entities.each do |entity|
      counts[entity] = dataset[entity] ? dataset[entity].length : 0
      min = (entity == :api_keys || entity == :invitations) ? 0 : 1
      if counts[entity] < min
        violations << "row count below minimum for #{entity}: #{counts[entity]} < #{min}"
      end
    end

    orgs = (dataset[:organizations] || []).map { |o| [o.id, o] }.to_h
    users = (dataset[:users] || []).map { |u| [u.id, u] }.to_h
    projects = (dataset[:projects] || []).map { |p| [p.id, p] }.to_h

    org_members = {}
    member_emails = {}
    membership_joined_at = {}

    seen_org_ids = {}
    (dataset[:organizations] || []).each do |org|
      violations << "duplicate organizations.id: #{org.id}" if seen_org_ids[org.id]
      seen_org_ids[org.id] = true
    end

    seen_emails = {}
    (dataset[:users] || []).each do |user|
      email = user.email.downcase
      violations << "duplicate user.email: #{email}" if seen_emails[email]
      seen_emails[email] = true
    end

    (dataset[:memberships] || []).each do |m|
      org = orgs[m.org_id]
      user = users[m.user_id]
      if org.nil?
        violations << "membership missing org: #{m.id}"
        next
      end
      if user.nil?
        violations << "membership missing user: #{m.id}"
        next
      end

      org_members[org.id] ||= {}
      org_members[org.id][user.id] = true
      member_emails[org.id] ||= {}
      member_emails[org.id][user.email.downcase] = true

      joined_at = Time.parse(m.joined_at)
      membership_joined_at[[org.id, user.id]] = joined_at
      org_created = Time.parse(org.created_at)
      if joined_at < org_created
        violations << "Rule A violated by membership #{m.id}"
      end
      if m.invited_by && !users.key?(m.invited_by)
        violations << "membership invited_by missing user: #{m.id}"
      end
    end

    (dataset[:projects] || []).each do |p|
      org = orgs[p.org_id]
      if org.nil?
        violations << "project missing org: #{p.id}"
        next
      end
      p_created = Time.parse(p.created_at)
      org_created = Time.parse(org.created_at)
      if p_created < org_created
        violations << "Rule B violated by project #{p.id}"
      end
      if !org_members.dig(p.org_id, p.created_by)
        violations << "Rule C violated by project #{p.id}"
      end
    end

    membership_ids = (dataset[:memberships] || []).map(&:id).to_h { |id| [id, true] }
    api_key_ids = (dataset[:api_keys] || []).map(&:id).to_h { |id| [id, true] }
    invitation_ids = (dataset[:invitations] || []).map(&:id).to_h { |id| [id, true] }

    (dataset[:audit_events] || []).each do |e|
      org = orgs[e.org_id]
      project = projects[e.project_id]
      if org.nil?
        violations << "audit event missing org: #{e.id}"
        next
      end
      if project.nil?
        violations << "audit event missing project: #{e.id}"
        next
      end
      if !org_members.dig(e.org_id, e.user_id)
        violations << "Rule D violated by audit event #{e.id}"
      end
      if project.org_id != e.org_id
        violations << "Rule E violated by audit event #{e.id}"
      end

      e_ts = Time.parse(e.ts)
      p_created = Time.parse(project.created_at)
      if e_ts < p_created
        violations << "Rule F violated by audit event #{e.id}"
      end
      
      joined_at = membership_joined_at[[e.org_id, e.user_id]]
      if joined_at && e_ts < joined_at
        violations << "audit event before membership joined_at: #{e.id}"
      end

      rt = e.resource_type
      rid = e.resource_id
      if rt == "project" && !projects.key?(rid)
        violations << "audit event resource project missing: #{e.id}"
      elsif rt == "user" && !users.key?(rid)
        violations << "audit event resource user missing: #{e.id}"
      elsif rt == "membership" && !membership_ids[rid]
        violations << "audit event resource membership missing: #{e.id}"
      elsif rt == "api_key" && !api_key_ids[rid]
        violations << "audit event resource api_key missing: #{e.id}"
      elsif rt == "invitation" && !invitation_ids[rid]
        violations << "audit event resource invitation missing: #{e.id}"
      end
    end

    seen_key_prefixes = {}
    (dataset[:api_keys] || []).each do |ak|
      if !org_members.dig(ak.org_id, ak.created_by)
        violations << "Rule G violated by api_key #{ak.id}"
      end
      prefix = ak.key_prefix
      if seen_key_prefixes[prefix]
        violations << "duplicate api_key.key_prefix: #{prefix}"
      end
      seen_key_prefixes[prefix] = true
      
      if ak.last_used_at
        created_at = Time.parse(ak.created_at)
        last_used_at = Time.parse(ak.last_used_at)
        if last_used_at < created_at
          violations << "api_key last_used_at before created_at: #{ak.id}"
        end
      end
    end

    (dataset[:invitations] || []).each do |inv|
      if !org_members.dig(inv.org_id, inv.invited_by)
        violations << "Rule H violated by invitation #{inv.id}"
      end
      email = inv.invited_email.downcase
      if member_emails.dig(inv.org_id, email)
        violations << "Rule I violated by invitation #{inv.id}"
      end
    end

    ValidationReport.new(
      ok: violations.empty?,
      violations: violations,
      counts: counts,
      seed: -1,
      profile_name: "unknown"
    )
  end

  def self.print_report(report)
    puts "Validation summary"
    puts "=================="
    puts "FK and cross-field checks: #{report.ok ? 'PASS' : 'FAIL'}"
    report.counts.each do |entity, count|
      status = count >= ([:api_keys, :invitations].include?(entity) ? 0 : 1) ? 'PASS' : 'FAIL'
      puts "Row count #{entity}: #{status} (#{count})"
    end
    unless report.violations.empty?
      puts "Violations:"
      report.violations.each do |v|
        puts "- #{v}"
      end
    end
  end
end