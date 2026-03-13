require "json"
require "hanami/action"

require_relative "../../../lib/ruby_hanami_example/persistence"

module RubyHanamiExample
  module Actions
    module Reports
      class Show < Hanami::Action
        def handle(request, response)
          tenant_id = request.params[:tenant_id].to_s
          snapshot = RubyHanamiExample::Persistence.report_for(tenant_id)

          response.format = :json
          response.body = JSON.generate(
            service: "ruby-hanami-example",
            tenant_id: tenant_id,
            reports: [snapshot],
          )
        end
      end
    end
  end
end
