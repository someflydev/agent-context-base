defmodule AnalyticsWorkbench.Charts.LatencyBoxplotTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Charts.LatencyBoxplot

  @agg %{
    services: ["auth"],
    p50s: [20.0],
    p95s: [50.0],
    p99s: [100.0]
  }

  test "build_figure returns expected shape" do
    fig = LatencyBoxplot.build_figure(@agg)
    assert fig.data |> hd() |> Map.get(:type) == "box"
  end
end
