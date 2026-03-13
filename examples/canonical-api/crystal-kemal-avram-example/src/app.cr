require "json"
require "kemal"

SERVICE_NAME = "crystal-kemal-avram-example"
PORT = ENV.fetch("PORT", "3000").to_i

struct HealthSnapshot
  include JSON::Serializable

  getter status : String
  getter service : String

  def initialize(@status : String, @service : String)
  end
end

struct ReportSummary
  include JSON::Serializable

  getter report_id : String
  getter total_events : Int32
  getter status : String

  def initialize(@report_id : String, @total_events : Int32, @status : String)
  end
end

struct ReportEnvelope
  include JSON::Serializable

  getter service : String
  getter tenant_id : String
  getter reports : Array(ReportSummary)

  def initialize(@service : String, @tenant_id : String, @reports : Array(ReportSummary))
  end
end

struct SeriesPoint
  include JSON::Serializable

  getter x : String
  getter y : Int32

  def initialize(@x : String, @y : Int32)
  end
end

struct MetricSeries
  include JSON::Serializable

  getter name : String
  getter points : Array(SeriesPoint)

  def initialize(@name : String, @points : Array(SeriesPoint))
  end
end

struct ChartPayload
  include JSON::Serializable

  getter metric : String
  getter series : Array(MetricSeries)

  def initialize(@metric : String, @series : Array(MetricSeries))
  end
end

struct ReportSnapshot
  getter tenant_id : String
  getter report_id : String
  getter total_events : Int32
  getter status : String

  def initialize(@tenant_id : String, @report_id : String, @total_events : Int32, @status : String)
  end
end

struct MetricPoint
  getter metric : String
  getter bucket_day : String
  getter total : Int32

  def initialize(@metric : String, @bucket_day : String, @total : Int32)
  end
end

class SeedStore
  REPORTS = [
    ReportSnapshot.new("acme", "daily-signups", 42, "ready"),
    ReportSnapshot.new("globex", "ops-latency", 17, "warming"),
  ]

  METRIC_POINTS = [
    MetricPoint.new("signups", "2026-03-01", 18),
    MetricPoint.new("signups", "2026-03-02", 24),
    MetricPoint.new("signups", "2026-03-03", 31),
  ]

  def self.fetch_report(tenant_id : String) : ReportSummary
    snapshot = REPORTS.find { |report| report.tenant_id == tenant_id }
    if snapshot
      ReportSummary.new(snapshot.report_id, snapshot.total_events, snapshot.status)
    else
      ReportSummary.new("daily-signups", 42, "ready")
    end
  end

  def self.fetch_series(metric : String) : Array(SeriesPoint)
    points = METRIC_POINTS
      .select { |point| point.metric == metric }
      .map { |point| SeriesPoint.new(point.bucket_day, point.total) }

    return points unless points.empty?

    [
      SeriesPoint.new("2026-03-01", 18),
      SeriesPoint.new("2026-03-02", 24),
      SeriesPoint.new("2026-03-03", 31),
    ]
  end
end

def render_report_card(tenant_id : String, total_events : Int32, status : String) : String
  <<-HTML
  <section id="report-card-#{tenant_id}" class="report-card" hx-swap-oob="true">
    <strong>Tenant #{tenant_id}</strong>
    <span>#{total_events} events in the last hour</span>
    <small>Status: #{status}</small>
  </section>
  HTML
end

get "/healthz" do |env|
  env.response.content_type = "application/json"
  HealthSnapshot.new("ok", SERVICE_NAME).to_json
end

get "/api/reports/:tenant_id" do |env|
  tenant_id = env.params.url["tenant_id"]
  env.response.content_type = "application/json"
  ReportEnvelope.new(
    SERVICE_NAME,
    tenant_id,
    [SeedStore.fetch_report(tenant_id)]
  ).to_json
end

get "/fragments/report-card/:tenant_id" do |env|
  tenant_id = env.params.url["tenant_id"]
  report = SeedStore.fetch_report(tenant_id)
  env.response.content_type = "text/html; charset=utf-8"
  render_report_card(tenant_id, report.total_events, report.status)
end

get "/data/chart/:metric" do |env|
  metric = env.params.url["metric"]
  env.response.content_type = "application/json"
  ChartPayload.new(
    metric,
    [MetricSeries.new(metric, SeedStore.fetch_series(metric))]
  ).to_json
end

Kemal.config.port = PORT
Kemal.run
