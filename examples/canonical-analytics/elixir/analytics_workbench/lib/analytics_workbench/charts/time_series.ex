defmodule AnalyticsWorkbench.Charts.TimeSeries do
  def build_figure(agg) do
    data = Enum.map(agg.by_environment, fn {env, counts} ->
      %{
        type: "scatter",
        mode: "lines+markers",
        name: env,
        x: agg.dates,
        y: counts,
        hovertemplate: "%{y} events<br>%{x}<extra></extra>"
      }
    end)

    total_count = Enum.sum(agg.counts)

    %{
      data: data,
      layout: %{
        title: %{text: "Event Volume Over Time"},
        xaxis: %{title: %{text: "Date"}},
        yaxis: %{title: %{text: "Event Count"}}
      },
      meta: %{
        total_count: total_count,
        generated_at: DateTime.utc_now() |> DateTime.to_iso8601()
      }
    }
  end
end
