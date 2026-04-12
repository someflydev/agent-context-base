require "dry-validation"
require "dry/validation/contract"

class SyncRunContract < Dry::Validation::Contract
  params do
    required(:run_id).filled(:string)
    required(:workspace_id).filled(:string)
    required(:status).filled(:string, included_in?: %w[pending running succeeded failed cancelled])
    required(:trigger).filled(:string, included_in?: %w[manual scheduled webhook])
    optional(:started_at).maybe(:string)
    optional(:finished_at).maybe(:string)
    optional(:duration_ms).maybe(:integer)
    optional(:records_ingested).maybe(:integer)
    optional(:error_code).maybe(:string)
  end

  rule(:duration_ms) do
    next if values[:duration_ms].nil?

    key.failure("must be >= 0") if values[:duration_ms].negative?
  end

  rule(:records_ingested) do
    next if values[:records_ingested].nil?

    key.failure("must be between 0 and 10000000") unless values[:records_ingested].between?(0, 10_000_000)
  end

  rule(:finished_at, :started_at) do
    if values[:finished_at]
      key(:started_at).failure("must be present when finished_at is set") unless values[:started_at]
      if values[:started_at]
        key(:finished_at).failure("must be after started_at") if values[:finished_at] < values[:started_at]
      end
    end
  end

  rule(:duration_ms, :finished_at) do
    if values[:finished_at] && values[:duration_ms].nil?
      key(:duration_ms).failure("is required when finished_at is set")
    end
  end

  rule(:error_code, :status) do
    if values[:status] == "failed"
      key(:error_code).failure("must be present when status is failed") if values[:error_code].nil? || values[:error_code].empty?
    elsif !values[:error_code].nil?
      key(:error_code).failure("must be nil unless status is failed")
    end
  end
end
