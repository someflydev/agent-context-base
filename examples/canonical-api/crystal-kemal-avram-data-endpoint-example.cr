require "json"
require "kemal"
require "avram"

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

class MetricPoint < BaseModel
  table do
    column metric : String
    column bucket_day : String
    column total : Int32
  end
end

class MetricPointQuery < MetricPoint::BaseQuery
  def for_metric(metric_name : String)
    metric(metric_name)
  end
end

get "/data/chart/:metric" do |env|
  metric = env.params.url["metric"]
  points = MetricPointQuery.new.for_metric(metric).map do |row|
    SeriesPoint.new(row.bucket_day, row.total)
  end

  points = [
    SeriesPoint.new("2026-03-01", 18),
    SeriesPoint.new("2026-03-02", 24),
    SeriesPoint.new("2026-03-03", 31),
  ] if points.empty?

  env.response.content_type = "application/json"
  ChartPayload.new(metric, [MetricSeries.new(metric, points)]).to_json
end
