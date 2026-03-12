defmodule ExampleWeb.ReportController do
  use ExampleWeb, :controller

  alias Example.Reporting

  def index(conn, %{"tenant_id" => tenant_id} = params) do
    limit =
      params
      |> Map.get("limit", "20")
      |> String.to_integer()
      |> min(100)

    summaries = Reporting.list_recent_reports(tenant_id, limit: limit)
    render(conn, :index, tenant_id: tenant_id, summaries: summaries)
  end
end

