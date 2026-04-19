defmodule AnalyticsWorkbench.Analytics.HeatmapTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Analytics.Heatmap
  alias AnalyticsWorkbench.Filters

  @events [
    %{timestamp: "2023-01-01T10:00:00Z", count: 5},
    %{timestamp: "2023-01-02T10:00:00Z", count: 10}
  ]

  test "aggregate_event_heatmap returns expected shape" do
    result = Heatmap.aggregate_event_heatmap(@events, %Filters{})
    assert Enum.member?(result.hours, 10)
    assert is_list(result.counts)
  end

  test "empty input returns zero-value result" do
    result = Heatmap.aggregate_event_heatmap([], %Filters{})
    # The implementation returns a 7x24 grid of zeros for empty input
    assert length(result.counts) == 7
    assert Enum.all?(result.counts, fn row -> length(row) == 24 and Enum.sum(row) == 0 end)
  end
end
