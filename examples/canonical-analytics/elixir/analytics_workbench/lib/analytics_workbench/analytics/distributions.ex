defmodule AnalyticsWorkbench.Analytics.Distributions do
  alias AnalyticsWorkbench.Filters

  def aggregate_latency_histogram(samples, %Filters{} = filters) do
    filtered = apply_filters(samples, filters)
    values = Enum.map(filtered, & &1.latency_ms) |> Enum.sort()

    %{
      values: values,
      p50: percentile(values, 50),
      p95: percentile(values, 95),
      p99: percentile(values, 99)
    }
  end

  def aggregate_latency_by_service(samples, services, %Filters{} = filters) do
    filtered = apply_filters(samples, filters)

    service_stats = Enum.map(services, fn s ->
      s_samples = Enum.filter(filtered, & to_string(&1.service) == s.name)
      values = Enum.map(s_samples, & &1.latency_ms) |> Enum.sort()
      {s.name, percentile(values, 50), percentile(values, 95), percentile(values, 99)}
    end)

    %{
      services: Enum.map(service_stats, & elem(&1, 0)),
      p50s: Enum.map(service_stats, & elem(&1, 1)),
      p95s: Enum.map(service_stats, & elem(&1, 2)),
      p99s: Enum.map(service_stats, & elem(&1, 3))
    }
  end

  defp percentile([], _), do: 0.0
  defp percentile(values, p) do
    idx = floor(length(values) * p / 100)
    idx = min(idx, length(values) - 1)
    Enum.at(values, idx) |> to_float() |> Float.round(2)
  end

  defp to_float(val) when is_integer(val), do: val / 1
  defp to_float(val), do: val

  defp apply_filters(samples, filters) do
    samples
    |> filter_by_multi(:service, filters.services)
    |> filter_by_multi(:environment, filters.environment)
  end

  defp filter_by_multi(events, _key, []), do: events
  defp filter_by_multi(events, key, values) do
    Enum.filter(events, &(to_string(Map.get(&1, key)) in values))
  end
end
