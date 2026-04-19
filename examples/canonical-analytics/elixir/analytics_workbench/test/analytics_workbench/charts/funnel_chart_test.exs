defmodule AnalyticsWorkbench.Charts.FunnelChartTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Charts.FunnelChart

  @agg %{
    stages: ["a", "b"],
    counts: [100, 50],
    drop_off_rates: [0.0, 0.5]
  }

  test "build_figure returns expected shape" do
    fig = FunnelChart.build_figure(@agg)
    assert fig.data |> hd() |> Map.get(:type) == "funnel"
  end
end
