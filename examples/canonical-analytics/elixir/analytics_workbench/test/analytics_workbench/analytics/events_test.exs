defmodule AnalyticsWorkbench.Analytics.EventsTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Analytics.Events
  alias AnalyticsWorkbench.Filters

  @events [
    %{timestamp: "2023-01-01T10:00:00Z", environment: "production", service: "auth-service", count: 10},
    %{timestamp: "2023-01-01T11:00:00Z", environment: "staging", service: "auth-service", count: 5},
    %{timestamp: "2023-01-02T10:00:00Z", environment: "production", service: "billing-api", count: 20}
  ]

  test "aggregate_event_counts returns expected shape" do
    result = Events.aggregate_event_counts(@events, %Filters{})
    assert result.dates == ["2023-01-01", "2023-01-02"]
    assert result.counts == [15, 20]
    assert Map.has_key?(result.by_environment, "production")
    assert Map.has_key?(result.by_environment, "staging")
  end

  test "filter by environment narrows results" do
    filters = %Filters{environment: ["production"]}
    result = Events.aggregate_event_counts(@events, filters)
    assert result.counts == [10, 20]
  end

  test "aggregate with empty input returns zero-value result" do
    result = Events.aggregate_event_counts([], %Filters{})
    assert result.dates == []
    assert result.counts == []
    assert result.by_environment == %{}
  end
end
