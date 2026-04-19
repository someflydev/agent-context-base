defmodule AnalyticsWorkbench.Analytics.ServicesTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Analytics.Services
  alias AnalyticsWorkbench.Filters

  @services [
    %{name: "auth-service", environment: :production, error_rate: 0.05},
    %{name: "auth-service", environment: :staging, error_rate: 0.10},
    %{name: "billing-api", environment: :production, error_rate: 0.02}
  ]
  @events [
    %{service: "auth-service", count: 100},
    %{service: "billing-api", count: 200}
  ]

  test "aggregate_service_error_rates returns expected shape" do
    result = Services.aggregate_service_error_rates(@events, @services, %Filters{})
    assert result.services == ["auth-service", "billing-api"]
    # Floating point comparison
    assert_in_delta hd(result.error_rates), 0.075, 0.0001
    assert result.total_events == [100, 200]
  end

  test "filter by service narrows results" do
    filters = %Filters{services: ["billing-api"]}
    result = Services.aggregate_service_error_rates(@events, @services, filters)
    assert result.services == ["billing-api"]
  end

  test "aggregate with empty input returns zero-value result" do
    result = Services.aggregate_service_error_rates([], [], %Filters{})
    assert result.services == []
    assert result.error_rates == []
  end
end
