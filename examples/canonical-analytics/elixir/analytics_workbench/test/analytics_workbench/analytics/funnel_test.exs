defmodule AnalyticsWorkbench.Analytics.FunnelTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Analytics.Funnel
  alias AnalyticsWorkbench.Filters

  @sessions [
    %{funnel_stage: "completed_purchase"},
    %{funnel_stage: "added_payment"},
    %{funnel_stage: "visited_site"}
  ]

  test "aggregate_funnel_stages returns expected shape" do
    result = Funnel.aggregate_funnel_stages(@sessions, %Filters{})
    assert result.stages == ["visited_site", "signed_up", "added_payment", "completed_purchase"]
    # 3 total sessions
    # 3 reached visited_site
    # 2 reached signed_up (those who reached added_payment and completed_purchase)
    # 2 reached added_payment (those who reached added_payment and completed_purchase)
    # 1 reached completed_purchase
    assert result.counts == [3, 2, 2, 1]
  end

  test "empty input returns zero-value result" do
    result = Funnel.aggregate_funnel_stages([], %Filters{})
    assert result.counts == [0, 0, 0, 0]
  end
end
