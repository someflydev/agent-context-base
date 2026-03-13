require "hanami/action"

require_relative "../../../lib/ruby_hanami_example/persistence"
require_relative "../../views/report_cards/show"

module RubyHanamiExample
  module Actions
    module ReportCards
      class Show < Hanami::Action
        def handle(request, response)
          tenant_id = request.params[:tenant_id].to_s
          snapshot = RubyHanamiExample::Persistence.report_for(tenant_id)

          response.format = :html
          response.body = RubyHanamiExample::Views::ReportCards::Show.new.call(
            tenant_id: tenant_id,
            snapshot: snapshot,
          ).to_s
        end
      end
    end
  end
end
