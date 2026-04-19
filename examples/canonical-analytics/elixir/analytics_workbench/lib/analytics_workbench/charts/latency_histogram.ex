defmodule AnalyticsWorkbench.Charts.LatencyHistogram do
  def build_figure(agg) do
    trace = %{
      type: "histogram",
      x: agg.values,
      nbinsx: 30,
      name: "Latency",
      hovertemplate: "%{x}ms: %{y} samples<extra></extra>"
    }

    %{
      data: [trace],
      layout: %{
        title: %{text: "Latency Distribution"},
        xaxis: %{title: %{text: "Latency (ms)"}},
        yaxis: %{title: %{text: "Frequency"}},
        shapes: [
          %{
            type: "line",
            x0: agg.p50,
            x1: agg.p50,
            y0: 0,
            y1: 1,
            yref: "paper",
            line: %{color: "red", width: 2, dash: "dash"}
          }
        ],
        annotations: [
          %{
            x: agg.p50,
            y: 1,
            yref: "paper",
            text: "P50: #{agg.p50}ms",
            showarrow: false,
            xanchor: "left"
          }
        ]
      },
      meta: %{
        total_count: length(agg.values),
        p95: agg.p95,
        p99: agg.p99,
        generated_at: DateTime.utc_now() |> DateTime.to_iso8601()
      }
    }
  end
end
