defmodule AnalyticsWorkbench.Charts.ServiceBarTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Charts.ServiceBar

  @agg %{
    services: ["auth", "billing"],
    error_rates: [0.05, 0.02],
    total_events: [1000, 2000]
  }

  test "build_figure returns expected shape" do
    fig = ServiceBar.build_figure(@agg)
    assert length(fig.data) == 1
    assert fig.data |> hd() |> Map.get(:type) == "bar"
  end
end
