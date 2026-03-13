require "json"
require "hanami/action"
require "hanami/router"
require "sequel"

module RubyHanamiDataEndpointExample
  DB = Sequel.sqlite

  class MetricsRepo
    def self.series_for(metric)
      rows = DB[:metric_points].where(metric: metric).order(:bucket_day).all
      return rows.map { |row| { x: row[:bucket_day], y: row[:total] } } unless rows.empty?

      [
        { x: "2026-03-01", y: 18 },
        { x: "2026-03-02", y: 24 },
        { x: "2026-03-03", y: 31 },
      ]
    end
  end

  class ShowChart < Hanami::Action
    def handle(request, response)
      metric = request.params[:metric].to_s

      response.format = :json
      response.body = JSON.generate(
        metric: metric,
        series: [
          {
            name: metric,
            points: MetricsRepo.series_for(metric),
          },
        ],
      )
    end
  end

  Routes = Hanami::Router.new do
    get "/data/chart/:metric", to: ShowChart.new
  end
end
