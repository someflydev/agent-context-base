defmodule AnalyticsWorkbench.Charts.IncidentBarTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Charts.IncidentBar

  @agg %{
    severities: ["critical", "high"],
    counts: [5, 10],
    mttr_by_severity: %{"critical" => 2.0, "high" => 4.0}
  }

  test "build_figure returns expected shape" do
    fig = IncidentBar.build_figure(@agg)
    assert fig.data |> hd() |> Map.get(:type) == "bar"
  end
end
