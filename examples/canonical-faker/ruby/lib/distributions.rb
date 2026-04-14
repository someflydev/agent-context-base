module Distributions
  PLAN_WEIGHTS = { "free" => 50, "pro" => 35, "enterprise" => 15 }.freeze
  REGION_WEIGHTS = { "us-east" => 40, "us-west" => 25, "eu-west" => 20, "ap-southeast" => 15 }.freeze
  LOCALE_WEIGHTS = { "en-US" => 60, "en-GB" => 20, "de-DE" => 10, "fr-FR" => 10 }.freeze
  ROLE_WEIGHTS = { "owner" => 5, "admin" => 10, "member" => 60, "viewer" => 25 }.freeze
  PROJECT_STATUS_WEIGHTS = { "active" => 60, "archived" => 25, "draft" => 15 }.freeze
  AUDIT_ACTION_WEIGHTS = { "updated" => 35, "created" => 20, "exported" => 15, "invited" => 12, "archived" => 10, "deleted" => 8 }.freeze
  RESOURCE_TYPE_WEIGHTS = { "project" => 35, "user" => 15, "membership" => 25, "api_key" => 10, "invitation" => 15 }.freeze
  INVITATION_ROLE_WEIGHTS = { "admin" => 15, "member" => 65, "viewer" => 20 }.freeze

  TIMEZONE_BY_LOCALE = {
    "en-US" => "America/New_York",
    "en-GB" => "Europe/London",
    "de-DE" => "Europe/Berlin",
    "fr-FR" => "Europe/Paris"
  }.freeze

  def self.weighted_choice(weights_hash, rng)
    total = weights_hash.values.sum
    target = rng.rand(total)
    cumulative = 0
    weights_hash.each do |value, weight|
      cumulative += weight
      return value if target < cumulative
    end
  end

  def self.bounded_count(rng, min, max, mode)
    u = rng.rand
    c = (mode - min).to_f / (max - min)
    if u < c
      (min + Math.sqrt(u * (max - min) * (mode - min))).round
    else
      (max - Math.sqrt((1 - u) * (max - min) * (max - mode))).round
    end
  end
end