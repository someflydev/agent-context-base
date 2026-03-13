require "json"
require "kemal"
require "avram"

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

class ReportSnapshot < BaseModel
  table do
    column tenant_id : String
    column report_id : String
    column total_events : Int32
    column status : String
  end
end

class ReportSnapshotQuery < ReportSnapshot::BaseQuery
  def for_tenant(tenant_id : String)
    tenant_id(tenant_id)
  end
end

get "/api/reports/:tenant_id" do |env|
  tenant_id = env.params.url["tenant_id"]
  snapshot = ReportSnapshotQuery.new.for_tenant(tenant_id).first?

  payload =
    if snapshot
      ReportEnvelope.new(
        "crystal-kemal-avram",
        tenant_id,
        [ReportSummary.new(snapshot.report_id, snapshot.total_events, snapshot.status)]
      )
    else
      ReportEnvelope.new(
        "crystal-kemal-avram",
        tenant_id,
        [ReportSummary.new("daily-signups", 42, "ready")]
      )
    end

  env.response.content_type = "application/json"
  payload.to_json
end
