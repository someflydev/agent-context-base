defmodule AnalyticsWorkbench.Charts.ServiceBar do
  def build_figure(agg) do
    trace = %{
      type: "bar",
      orientation: "h",
      x: agg.error_rates,
      y: agg.services,
      hovertemplate: "%{y}: %{x|%}<extra></extra>"
    }

    %{
      data: [trace],
      layout: %{
        title: %{text: "Error Rate by Service"},
        xaxis: %{title: %{text: "Error Rate"}, tickformat: ".1%"},
        yaxis: %{title: %{text: "Service"}, autoresize: true}
      },
      meta: %{
        total_count: Enum.sum(agg.total_events),
        generated_at: DateTime.utc_now() |> DateTime.to_iso8601()
      }
    }
  end
end
