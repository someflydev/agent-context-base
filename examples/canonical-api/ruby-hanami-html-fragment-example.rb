require "hanami/action"
require "hanami/router"
require "hanami/view"

module RubyHanamiHtmlFragmentExample
  class ReportCardView < Hanami::View
    config.paths = [File.expand_path("templates", __dir__)]
    config.template = "report_cards/show"
    config.layout = false

    expose :tenant_id
    expose :snapshot
  end

  class ShowReportCard < Hanami::Action
    def handle(request, response)
      tenant_id = request.params[:tenant_id].to_s
      snapshot = { report_id: "daily-signups", total_events: 42, status: "ready" }

      response.format = :html
      response.body = ReportCardView.new.call(tenant_id: tenant_id, snapshot: snapshot).to_s
    end
  end

  Routes = Hanami::Router.new do
    get "/fragments/report-card/:tenant_id", to: ShowReportCard.new
  end
end
