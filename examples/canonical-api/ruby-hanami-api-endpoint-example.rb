require "json"
require "hanami/action"
require "hanami/router"
require "sequel"

module RubyHanamiApiEndpointExample
  DB = Sequel.sqlite

  class ReportsRepo
    def self.fetch(tenant_id)
      DB[:reports].where(tenant_id: tenant_id).first || {
        report_id: "daily-signups",
        total_events: 42,
        status: "ready",
      }
    end
  end

  class ShowReport < Hanami::Action
    def handle(request, response)
      tenant_id = request.params[:tenant_id].to_s
      snapshot = ReportsRepo.fetch(tenant_id)

      response.format = :json
      response.body = JSON.generate(
        service: "ruby-hanami",
        tenant_id: tenant_id,
        reports: [snapshot],
      )
    end
  end

  Routes = Hanami::Router.new do
    get "/api/reports/:tenant_id", to: ShowReport.new
  end
end
