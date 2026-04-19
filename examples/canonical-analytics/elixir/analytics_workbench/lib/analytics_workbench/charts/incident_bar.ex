defmodule AnalyticsWorkbench.Charts.IncidentBar do
  def build_figure(agg) do
    trace = %{
      type: "bar",
      x: agg.severities,
      y: agg.counts,
      marker: %{
        color: Enum.map(agg.severities, fn
          "sev1" -> "red"
          "sev2" -> "orange"
          "sev3" -> "yellow"
          _ -> "gray"
        end)
      },
      hovertemplate: "%{x}: %{y} incidents<extra></extra>"
    }

    %{
      data: [trace],
      layout: %{
        title: %{text: "Incidents by Severity"},
        xaxis: %{title: %{text: "Severity"}},
        yaxis: %{title: %{text: "Incident Count"}}
      },
      meta: %{
        total_count: Enum.sum(agg.counts),
        generated_at: DateTime.utc_now() |> DateTime.to_iso8601()
      }
    }
  end
end
