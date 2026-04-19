defmodule AnalyticsWorkbench.Analytics.DistributionsTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Analytics.Distributions
  alias AnalyticsWorkbench.Filters

  @samples [
    %{latency_ms: 100.0, service: "auth", environment: "prod"},
    %{latency_ms: 200.0, service: "auth", environment: "prod"},
    %{latency_ms: 300.0, service: "auth", environment: "prod"},
    %{latency_ms: 400.0, service: "auth", environment: "prod"},
    %{latency_ms: 500.0, service: "auth", environment: "prod"}
  ]

  test "aggregate_latency_histogram returns expected shape" do
    result = Distributions.aggregate_latency_histogram(@samples, %Filters{})
    assert result.p50 == 300.0
    assert result.values == [100.0, 200.0, 300.0, 400.0, 500.0]
  end

  test "aggregate_latency_by_service returns expected shape" do
    services = [%{name: "auth", environment: "prod"}]
    result = Distributions.aggregate_latency_by_service(@samples, services, %Filters{})
    assert result.services == ["auth"]
    assert result.p50s == [300.0]
  end

  test "empty input returns zero-value result" do
    result = Distributions.aggregate_latency_histogram([], %Filters{})
    assert result.values == []
    assert result.p50 == 0.0
  end
end
