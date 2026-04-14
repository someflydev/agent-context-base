require 'ffaker'
require 'securerandom'
require 'date'
require_relative 'domain'
require_relative 'profiles'
require_relative 'distributions'

class FfakerPipeline
  def self.generate(profile)
    # ffaker seeding:
    FFaker::Random.seed = profile.seed
    rng = Random.new(profile.seed)
    
    dataset = { organizations: [] }
    seen_slugs = {}
    seen_org_emails = {}

    profile.num_orgs.times do
      name = FFaker::Company.name
      slug = name.downcase.gsub(/[^a-z0-9]/, '-').gsub(/-+/, '-').chomp('-')
      slug = "tenantcore" if slug.empty?
      
      base_slug = slug
      suffix = 1
      while seen_slugs.key?(slug)
        suffix += 1
        slug = "#{base_slug}-#{suffix}"
      end
      seen_slugs[slug] = true

      email = FFaker::Internet.email
      while seen_org_emails.key?(email)
        email = FFaker::Internet.email
      end
      seen_org_emails[email] = true

      created_at = Time.now.utc - rng.rand(0..(3 * 365 * 24 * 60 * 60))

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
    end

    dataset
  end
end