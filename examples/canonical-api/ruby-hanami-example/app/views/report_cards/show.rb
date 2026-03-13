require "hanami/view"

module RubyHanamiExample
  module Views
    module ReportCards
      class Show < Hanami::View
        config.paths = [File.expand_path("../../templates", __dir__)]
        config.template = "report_cards/show"
        config.layout = false

        expose :tenant_id
        expose :snapshot
      end
    end
  end
end
