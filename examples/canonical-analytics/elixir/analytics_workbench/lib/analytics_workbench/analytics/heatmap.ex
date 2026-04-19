defmodule AnalyticsWorkbench.Analytics.Heatmap do
  alias AnalyticsWorkbench.Filters

  def aggregate_event_heatmap(events, %Filters{} = filters) do
    filtered = apply_filters(events, filters)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = Enum.to_list(0..23)

    counts = Enum.map(days, fn d ->
      Enum.map(hours, fn h ->
        Enum.count(filtered, fn e ->
          # Parse timestamp to get day and hour
          # In real app use a library, here we assume ISO8601
          # and we might need to calculate day of week
          # For simplicity in the example, we'll use a placeholder or dummy calculation
          # if the fixture doesn't have day/hour explicitly.
          # But the spec says hours: [Integer], days: [String], counts: [[Integer]]
          # Let's assume we can extract hour from timestamp "YYYY-MM-DDTHH:MM:SSZ"
          dt = e.timestamp
          hour = String.slice(dt, 11, 2) |> String.to_integer()
          # Day of week is harder with pure strings, let's just use a dummy day grouping
          # based on the date for this example.
          # Or better, use Date.from_iso8601 and Date.day_of_week
          {:ok, date} = String.slice(dt, 0, 10) |> Date.from_iso8601()
          day_idx = Date.day_of_week(date) # 1..7
          day_name = Enum.at(days, day_idx - 1)

          day_name == d and hour == h
        end)
      end)
    end)

    %{hours: hours, days: days, counts: counts}
  end

  defp apply_filters(events, filters) do
    events
    |> filter_by_date(filters)
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
