require "dry-validation"
require "dry/validation/contract"
require "uri"

class ReviewRequestContract < Dry::Validation::Contract
  params do
    required(:request_id).filled(:string)
    required(:workspace_id).filled(:string)
    required(:reviewer_emails).array(:string)
    required(:content_ids).array(:string)
    required(:priority).filled(:string, included_in?: %w[low normal high critical])
    optional(:due_at).maybe(:string)
    optional(:notes).maybe(:string)
  end

  rule(:reviewer_emails) do
    key.failure("must contain 1..5 reviewer emails") unless value.length.between?(1, 5)
    key.failure("must be unique") unless value.uniq.length == value.length
    value.each_with_index do |email, index|
      key([:reviewer_emails, index]).failure("must be a valid email") unless email.match?(URI::MailTo::EMAIL_REGEXP)
    end
  end

  rule(:content_ids) do
    key.failure("must contain 1..50 content ids") unless value.length.between?(1, 50)
    key.failure("must be unique") unless value.uniq.length == value.length
  end

  rule(:priority, :due_at) do
    if values[:priority] == "critical" && values[:due_at].nil?
      key(:due_at).failure("is required when priority is critical")
    end
  end

  rule(:notes) do
    next if value.nil?

    key.failure("must be <= 2000 chars") if value.length > 2000
  end
end
