defmodule AnalyticsWorkbench.Charts.TimeSeriesTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Charts.TimeSeries

  @agg %{
    dates: ["2023-01-01", "2023-01-02"],
    counts: [100, 200],
    by_environment: %{"production" => [60, 140], "staging" => [40, 60]}
  }

  test "build_figure returns a map with data key" do
    fig = TimeSeries.build_figure(@agg)
    assert is_list(fig.data)
    assert length(fig.data) == 2 # one per environment
  end

  test "build_figure layout title is non-empty" do
    fig = TimeSeries.build_figure(@agg)
    assert fig.layout.title.text =~ "Volume"
  end
end
