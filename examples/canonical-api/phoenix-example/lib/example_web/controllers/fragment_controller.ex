defmodule ExampleWeb.FragmentController do
  use ExampleWeb, :controller

  alias Example.Reporting

  def show(conn, %{"tenant_id" => tenant_id}) do
    [report | _] = Reporting.list_recent_reports(tenant_id, limit: 1)
    html(conn, render_fragment(tenant_id, report.total_events, report.status))
  end

  defp render_fragment(tenant_id, total_events, status) do
    """
    <section id="report-card-#{tenant_id}" class="report-card" hx-swap-oob="true">
      <strong>Tenant #{tenant_id}</strong>
      <span>#{total_events} events in the last hour</span>
      <small>Status: #{status}</small>
    </section>
    """
  end
end
