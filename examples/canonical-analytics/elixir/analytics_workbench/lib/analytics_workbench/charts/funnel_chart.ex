defmodule AnalyticsWorkbench.Charts.FunnelChart do
  def build_figure(agg) do
    trace = %{
      type: "funnel",
      y: agg.stages,
      x: agg.counts,
      textinfo: "value+percent previous",
      hovertemplate: "%{y}: %{x} sessions<extra></extra>"
    }

    %{
      data: [trace],
      layout: %{
        title: %{text: "Conversion Funnel"},
        yaxis: %{title: %{text: "Stage"}}
      },
      meta: %{
        total_count: List.first(agg.counts) || 0,
        generated_at: DateTime.utc_now() |> DateTime.to_iso8601()
      }
    }
  end
end
