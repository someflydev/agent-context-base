require "dry-schema"

SyncRunSchema = Dry::Schema.JSON do
  required(:run_id).filled(:string)
  required(:workspace_id).filled(:string)
  required(:status).filled(:string, included_in?: %w[pending running succeeded failed cancelled])
  required(:trigger).filled(:string, included_in?: %w[manual scheduled webhook])
  optional(:started_at).maybe(:string)
  optional(:finished_at).maybe(:string)
  optional(:duration_ms).maybe(:integer, gteq?: 0)
  optional(:records_ingested).maybe(:integer, gteq?: 0, lteq?: 10_000_000)
  optional(:error_code).maybe(:string)
end
