require "kemal"
require "avram"

class ReportSnapshot < BaseModel
  table do
    column tenant_id : String
    column total_events : Int32
    column status : String
  end
end

class ReportSnapshotQuery < ReportSnapshot::BaseQuery
  def for_tenant(tenant_id : String)
    tenant_id(tenant_id)
  end
end

def render_report_card(tenant_id : String, total_events : Int32, status : String) : String
  <<-HTML
  <section id="report-card-#{tenant_id}" class="report-card" hx-swap-oob="true">
    <strong>Tenant #{tenant_id}</strong>
    <span>#{total_events} events processed</span>
    <small>Status: #{status}</small>
  </section>
  HTML
end

get "/fragments/report-card/:tenant_id" do |env|
  tenant_id = env.params.url["tenant_id"]
  snapshot = ReportSnapshotQuery.new.for_tenant(tenant_id).first?

  env.response.content_type = "text/html; charset=utf-8"
  render_report_card(
    tenant_id,
    snapshot.try(&.total_events) || 42,
    snapshot.try(&.status) || "ready"
  )
end
