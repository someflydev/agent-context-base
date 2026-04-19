defmodule AnalyticsWorkbench.Analytics.Funnel do
  alias AnalyticsWorkbench.Filters

  def aggregate_funnel_stages(sessions, %Filters{} = filters) do
    filtered = apply_filters(sessions, filters)

    stages = ["visited_site", "signed_up", "added_payment", "completed_purchase"]
    
    counts = Enum.map(stages, fn s ->
      # A session counts for a stage if it reached that stage or a later one.
      # For simplicity in this mock, we assume stages are in order and funnel_stage
      # represents the last completed stage.
      Enum.count(filtered, fn sess ->
        reached_stage?(to_string(sess.funnel_stage), s, stages)
      end)
    end)

    drop_off_rates = Enum.with_index(counts) |> Enum.map(fn {count, idx} ->
      if idx == 0 do
        0.0
      else
        prev_count = Enum.at(counts, idx - 1)
        if prev_count > 0, do: Float.round((prev_count - count) / prev_count, 4), else: 1.0
      end
    end)

    %{stages: stages, counts: counts, drop_off_rates: drop_off_rates}
  end

  defp reached_stage?(current_stage, target_stage, stages) do
    current_idx = Enum.find_index(stages, & &1 == current_stage) || -1
    target_idx = Enum.find_index(stages, & &1 == target_stage) || 0
    current_idx >= target_idx
  end

  defp apply_filters(sessions, filters) do
    sessions
    |> filter_by_multi(:environment, filters.environment)
  end

  defp filter_by_multi(events, _key, []), do: events
  defp filter_by_multi(events, key, values) do
    Enum.filter(events, &(to_string(Map.get(&1, key)) in values))
  end
end
