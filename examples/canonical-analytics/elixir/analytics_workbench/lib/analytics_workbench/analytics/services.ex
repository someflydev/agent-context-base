defmodule AnalyticsWorkbench.Analytics.Services do
  alias AnalyticsWorkbench.Filters

  def aggregate_service_error_rates(events, services, %Filters{} = filters) do
    filtered_services = services
      |> Enum.filter(fn s ->
        (filters.environment == [] or to_string(s.environment) in filters.environment) and
        (filters.services == [] or s.name in filters.services)
      end)

    if filtered_services == [] do
      %{services: [], error_rates: [], total_events: []}
    else
      # event counts per service
      event_counts = events
        |> Enum.group_by(& &1.service)
        |> Map.new(fn {service, service_events} ->
          {to_string(service), Enum.map(service_events, & &1.count) |> Enum.sum()}
        end)

      # Average error rates across environments for the same service
      agg = filtered_services
        |> Enum.group_by(& &1.name)
        |> Enum.map(fn {name, s_list} ->
          mean_error_rate = Enum.map(s_list, & &1.error_rate) |> Enum.sum() |> Kernel./(length(s_list))
          {name, mean_error_rate}
        end)
        |> Enum.sort_by(fn {_, rate} -> rate end, :desc)

      %{
        services: Enum.map(agg, & elem(&1, 0)),
        error_rates: Enum.map(agg, & elem(&1, 1)),
        total_events: Enum.map(agg, fn {name, _} -> Map.get(event_counts, name, 0) end)
      }
    end
  end
end
