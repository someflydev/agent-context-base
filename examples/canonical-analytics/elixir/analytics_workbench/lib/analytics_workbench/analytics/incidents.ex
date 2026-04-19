defmodule AnalyticsWorkbench.Analytics.Incidents do
  alias AnalyticsWorkbench.Filters

  def aggregate_incident_severity(incidents, %Filters{} = filters) do
    filtered = apply_filters(incidents, filters)

    severities = ["sev1", "sev2", "sev3"]
    
    counts = Enum.map(severities, fn s ->
      Enum.count(filtered, & to_string(&1.severity) == s)
    end)

    mttr_by_severity = Enum.map(severities, fn s ->
      s_incidents = Enum.filter(filtered, & to_string(&1.severity) == s)
      durations = Enum.map(s_incidents, & &1.mttr_mins)
      avg = if length(durations) > 0, do: Enum.sum(durations) / length(durations), else: 0.0
      {s, Float.round(avg, 2)}
    end) |> Map.new()

    %{severities: severities, counts: counts, mttr_by_severity: mttr_by_severity}
  end

  defp apply_filters(incidents, filters) do
    incidents
    |> filter_by_date(filters)
    |> filter_by_multi(:service, filters.services)
    |> filter_by_multi(:environment, filters.environment)
    |> filter_by_multi(:severity, filters.severity)
  end

  defp filter_by_date(events, %{date_from: from, date_to: to}) do
    events
    |> Enum.filter(fn e ->
      (is_nil(from) or from == "" or String.slice(e.timestamp, 0, 10) >= from) and
      (is_nil(to) or to == "" or String.slice(e.timestamp, 0, 10) <= to)
    end)
  end

  defp filter_by_multi(events, _key, []), do: events
  defp filter_by_multi(events, key, values) do
    Enum.filter(events, &(to_string(Map.get(&1, key)) in values))
  end
end
