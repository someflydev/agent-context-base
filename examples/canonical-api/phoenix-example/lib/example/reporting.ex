defmodule Example.Reporting do
  @reports %{
    "acme" => %{report_id: "daily-signups", total_events: 42, status: "ready"},
    "globex" => %{report_id: "ops-latency", total_events: 17, status: "warming"}
  }

  @fallback_report %{report_id: "daily-signups", total_events: 42, status: "ready"}

  @signups_series [
    %{x: "2026-03-01", y: 18},
    %{x: "2026-03-02", y: 24},
    %{x: "2026-03-03", y: 31}
  ]

  def list_recent_reports(tenant_id, opts \\ []) do
    limit = Keyword.get(opts, :limit, 20)
    report = Map.get(@reports, tenant_id, @fallback_report)
    [report] |> Enum.take(limit)
  end

  def series_for(metric) do
    case metric do
      "signups" -> @signups_series
      _other -> @signups_series
    end
  end
end
