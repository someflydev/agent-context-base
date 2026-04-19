defmodule AnalyticsWorkbench.Analytics.Events do
  alias AnalyticsWorkbench.Filters

  def aggregate_event_counts(events, %Filters{} = filters) do
    filtered = apply_filters(events, filters)

    # Group by date and environment
    grouped = Enum.group_by(filtered, fn e ->
      String.slice(e.timestamp, 0, 10)
    end)

    dates = Map.keys(grouped) |> Enum.sort()

    by_environment = filtered
      |> Enum.group_by(& &1.environment)
      |> Map.new(fn {env, env_events} ->
        env_counts = dates |> Enum.map(fn d ->
          env_events
          |> Enum.filter(& String.starts_with?(&1.timestamp, d))
          |> Enum.map(& &1.count)
          |> Enum.sum()
        end)
        {to_string(env), env_counts}
      end)

    counts = dates |> Enum.map(fn d ->
      filtered
      |> Enum.filter(& String.starts_with?(&1.timestamp, d))
      |> Enum.map(& &1.count)
      |> Enum.sum()
    end)

    %{dates: dates, counts: counts, by_environment: by_environment}
  end

  defp apply_filters(events, filters) do
    events
    |> filter_by_date(filters)
    |> filter_by_multi(:service, filters.services)
    |> filter_by_multi(:environment, filters.environment)
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
