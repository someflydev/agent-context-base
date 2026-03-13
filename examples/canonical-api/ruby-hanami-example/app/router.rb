require "hanami/router"

require_relative "actions/health/show"
require_relative "actions/reports/show"
require_relative "actions/report_cards/show"
require_relative "actions/charts/show"

module RubyHanamiExample
  App = Hanami::Router.new do
    get "/healthz", to: Actions::Health::Show.new
    get "/api/reports/:tenant_id", to: Actions::Reports::Show.new
    get "/fragments/report-card/:tenant_id", to: Actions::ReportCards::Show.new
    get "/data/chart/:metric", to: Actions::Charts::Show.new
  end
end
