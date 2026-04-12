require "dry-validation"
require "dry/validation/contract"

class WebhookPayloadContract < Dry::Validation::Contract
  params do
    required(:event_type).filled(:string, included_in?: ["sync.completed", "sync.failed", "workspace.suspended"])
    required(:payload_version).filled(:string, included_in?: %w[v1 v2 v3])
    required(:timestamp).filled(:string)
    required(:signature).filled(:string)
    required(:data).hash
  end

  rule(:signature) do
    key.failure("must be 64 lowercase hex chars") unless value.match?(/\A[a-f0-9]{64}\z/)
  end

  # dry-validation does not have native discriminated union support.
  # The rule block on :data checks event_type and validates the nested hash manually.
  rule(:data) do
    payload = values[:data]
    case values[:event_type]
    when "sync.completed"
      %i[run_id workspace_id duration_ms records_ingested].each do |field|
        key([:data, field]).failure("is required") unless payload.key?(field)
      end
    when "sync.failed"
      %i[run_id workspace_id error_code error_message].each do |field|
        key([:data, field]).failure("is required") unless payload.key?(field)
      end
    when "workspace.suspended"
      %i[workspace_id suspended_until reason].each do |field|
        key([:data, field]).failure("is required") unless payload.key?(field)
      end
    end
  end
end
