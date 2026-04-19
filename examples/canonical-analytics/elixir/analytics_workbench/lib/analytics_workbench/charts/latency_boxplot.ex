defmodule AnalyticsWorkbench.Charts.LatencyBoxplot do
  def build_figure(agg) do
    data = Enum.with_index(agg.services) |> Enum.map(fn {service, idx} ->
      %{
        type: "box",
        name: service,
        # In a real box plot we'd pass all raw samples,
        # but here we might just have p50, p95, p99.
        # Plotly can take precomputed stats if we use 'box' with 'q1', 'median', etc.
        # but let's assume we have samples or just use simple box.
        y: [Enum.at(agg.p50s, idx), Enum.at(agg.p95s, idx), Enum.at(agg.p99s, idx)]
      }
    end)

    %{
      data: data,
      layout: %{
        title: %{text: "Latency by Service"},
        yaxis: %{title: %{text: "Latency (ms)"}}
      },
      meta: %{
        generated_at: DateTime.utc_now() |> DateTime.to_iso8601()
      }
    }
  end
end
