require "dry-validation"
require "dry/validation/contract"
require "uri"

class WorkspaceConfigContract < Dry::Validation::Contract
  params do
    required(:id).filled(:string)
    required(:name).filled(:string)
    required(:slug).filled(:string)
    required(:owner_email).filled(:string)
    required(:plan).filled(:string, included_in?: %w[free pro enterprise])
    required(:max_sync_runs).filled(:integer)
    required(:settings).hash do
      required(:retry_max).filled(:integer)
      required(:timeout_seconds).filled(:integer)
      required(:notify_on_failure).filled(:bool)
      optional(:webhook_url).maybe(:string)
    end
    optional(:tags).array(:string)
    required(:created_at).filled(:string)
    optional(:suspended_until).maybe(:string)
  end

  rule(:name) do
    key.failure("must be 3..100 chars") unless value.length.between?(3, 100)
  end

  rule(:slug) do
    key.failure("must be a valid slug (lowercase, hyphens, digits)") unless
      value.match?(/\A[a-z][a-z0-9-]{1,48}[a-z0-9]\z/)
  end

  rule(:owner_email) do
    key.failure("must be a valid email") unless value.match?(URI::MailTo::EMAIL_REGEXP)
  end

  rule(:max_sync_runs) do
    key.failure("must be between 1 and 1000") unless value.between?(1, 1000)
  end

  rule(:settings) do
    settings = values[:settings]
    next unless settings

    key([:settings, :retry_max]).failure("must be between 0 and 10") unless settings[:retry_max].between?(0, 10)
    key([:settings, :timeout_seconds]).failure("must be between 10 and 3600") unless settings[:timeout_seconds].between?(10, 3600)
    if settings[:webhook_url] && settings[:webhook_url] !~ %r{\Ahttps?://}
      key([:settings, :webhook_url]).failure("must be a valid http/https URL")
    end
  end

  rule(:tags) do
    next unless values[:tags]

    key.failure("must have at most 20 tags") if values[:tags].length > 20
    values[:tags].each_with_index do |tag, index|
      key([:tags, index]).failure("each tag must be 1..50 chars") unless tag.length.between?(1, 50)
    end
  end

  rule(:max_sync_runs, :plan) do
    limit = case values[:plan]
            when "free" then 10
            when "pro" then 100
            else 1000
            end
    key(:max_sync_runs).failure("must be <= #{limit} for #{values[:plan]} plan") if values[:max_sync_runs] > limit
  end
end
