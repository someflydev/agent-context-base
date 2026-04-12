require "dry-schema"

WorkspaceConfigSchema = Dry::Schema.JSON do
  required(:id).filled(:string)
  required(:name).filled(:string, min_size?: 3, max_size?: 100)
  required(:slug).filled(:string)
  required(:owner_email).filled(:string)
  required(:plan).filled(:string, included_in?: %w[free pro enterprise])
  required(:max_sync_runs).filled(:integer, gt?: 0, lteq?: 1000)
  required(:settings).hash do
    required(:retry_max).filled(:integer, gteq?: 0, lteq?: 10)
    required(:timeout_seconds).filled(:integer, gteq?: 10, lteq?: 3600)
    required(:notify_on_failure).filled(:bool)
    optional(:webhook_url).maybe(:string)
  end
  optional(:tags).array(:string)
  required(:created_at).filled(:string)
  optional(:suspended_until).maybe(:string)
end

# dry-schema handles type coercion and structural validation.
# It does not handle complex cross-field rules or semantic validation.
# For those, wrap the schema in a dry-validation Contract.
