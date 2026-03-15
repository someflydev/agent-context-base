defmodule ExampleWeb.ReportController do
  use ExampleWeb, :controller

  alias Example.Reporting

  def index(conn, %{"tenant_id" => tenant_id} = params) do
    limit =
      Map.get(params, "limit", "20")
      |> String.to_integer()
      |> min(100)

    reports = Reporting.list_recent_reports(tenant_id, limit: limit)
    json(conn, %{service: "phoenix-example", tenant_id: tenant_id, reports: reports})
  end
end
