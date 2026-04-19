defmodule AnalyticsWorkbench.Charts.LatencyHistogramTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Charts.LatencyHistogram

  @agg %{
    values: [10.0, 20.0, 30.0],
    p50: 20.0,
    p95: 30.0,
    p99: 30.0
  }

  test "build_figure returns expected shape" do
    fig = LatencyHistogram.build_figure(@agg)
    assert fig.data |> hd() |> Map.get(:type) == "histogram"
  end
end
