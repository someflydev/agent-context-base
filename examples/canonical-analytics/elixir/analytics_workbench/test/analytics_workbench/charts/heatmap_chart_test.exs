defmodule AnalyticsWorkbench.Charts.HeatmapChartTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Charts.HeatmapChart

  @agg %{
    hours: [0, 1],
    days: ["Mon", "Tue"],
    counts: [[10, 20], [30, 40]]
  }

  test "build_figure returns expected shape" do
    fig = HeatmapChart.build_figure(@agg)
    assert fig.data |> hd() |> Map.get(:type) == "heatmap"
  end
end
