defmodule AnalyticsWorkbench.Analytics.IncidentsTest do
  use ExUnit.Case, async: true
  alias AnalyticsWorkbench.Analytics.Incidents
  alias AnalyticsWorkbench.Filters

  @incidents [
    %{severity: "sev1", mttr_mins: 120.0},
    %{severity: "sev1", mttr_mins: 240.0},
    %{severity: "sev2", mttr_mins: 600.0}
  ]

  test "aggregate_incident_severity returns expected shape" do
    result = Incidents.aggregate_incident_severity(@incidents, %Filters{})
    assert Enum.member?(result.severities, "sev1")
    assert result.counts == [2, 1, 0] # sev1, sev2, sev3
    assert result.mttr_by_severity["sev1"] == 180.0 # (120+240)/2
  end

  test "empty input returns zero-value result" do
    result = Incidents.aggregate_incident_severity([], %Filters{})
    assert result.counts == [0, 0, 0]
  end
end
