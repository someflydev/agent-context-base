require "dry-validation"
require "dry/validation/contract"

class IngestionSourceContract < Dry::Validation::Contract
  params do
    required(:source_id).filled(:string)
    required(:source_type).filled(:string, included_in?: %w[http_poll webhook_push file_watch database_cdc])
    required(:config).hash
    required(:enabled).filled(:bool)
    optional(:poll_interval_seconds).maybe(:integer)
  end

  rule(:config, :source_type) do
    config = values[:config]
    case values[:source_type]
    when "http_poll"
      %i[url method headers].each do |field|
        key([:config, field]).failure("is required") unless config.key?(field)
      end
    when "webhook_push"
      %i[path secret].each do |field|
        key([:config, field]).failure("is required") unless config.key?(field)
      end
    when "file_watch"
      %i[path pattern].each do |field|
        key([:config, field]).failure("is required") unless config.key?(field)
      end
    when "database_cdc"
      %i[dsn table cursor_field].each do |field|
        key([:config, field]).failure("is required") unless config.key?(field)
      end
    end
  end

  rule(:poll_interval_seconds, :source_type) do
    if values[:source_type] == "http_poll"
      key(:poll_interval_seconds).failure("must be present and >= 60 for http_poll") if values[:poll_interval_seconds].nil? || values[:poll_interval_seconds] < 60
    elsif !values[:poll_interval_seconds].nil?
      key(:poll_interval_seconds).failure("must be nil unless source_type is http_poll")
    end
  end
end
