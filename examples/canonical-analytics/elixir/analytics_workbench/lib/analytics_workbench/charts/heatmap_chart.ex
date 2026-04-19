defmodule AnalyticsWorkbench.Charts.HeatmapChart do
  def build_figure(agg) do
    trace = %{
      type: "heatmap",
      x: agg.hours,
      y: agg.days,
      z: agg.counts,
      colorscale: "Blues"
    }

    %{
      data: [trace],
      layout: %{
        title: %{text: "Activity Heatmap"},
        xaxis: %{title: %{text: "Hour of Day"}},
        yaxis: %{title: %{text: "Day of Week"}}
      },
      meta: %{
        generated_at: DateTime.utc_now() |> DateTime.to_iso8601()
      }
    }
  end
end
