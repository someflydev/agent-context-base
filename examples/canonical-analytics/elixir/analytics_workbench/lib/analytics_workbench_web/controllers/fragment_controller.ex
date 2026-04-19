defmodule AnalyticsWorkbenchWeb.FragmentController do
  use AnalyticsWorkbenchWeb, :controller

  alias AnalyticsWorkbench.Data.Store
  alias AnalyticsWorkbench.Filters
  alias AnalyticsWorkbench.Analytics.{Events, Services, Distributions, Heatmap, Funnel, Incidents}
  alias AnalyticsWorkbench.Charts.{TimeSeries, ServiceBar, LatencyHistogram, HeatmapChart, FunnelChart, IncidentBar}

  def chart(conn, %{"view" => view} = params) do
    filters = Filters.parse(params)
    store = Store.get()
    {figure, _} = build_for_view(String.to_existing_atom(view), store, filters)
    figure_json = Jason.encode!(figure)
    
    render(conn, "chart.html", figure_json: figure_json)
  end

  def summary(conn, %{"view" => view} = params) do
    filters = Filters.parse(params)
    store = Store.get()
    {_, summary} = build_for_view(String.to_existing_atom(view), store, filters)
    
    render(conn, "summary.html", summary: summary, view: view)
  end

  def details(conn, %{"view" => "services", "service" => service_name} = _params) do
    store = Store.get()
    incidents = Enum.filter(store.incidents, & &1.services |> to_string() == service_name)
    
    render(conn, "details.html", incidents: incidents, service_name: service_name)
  end

  # Re-using logic from PageController or moving it to a shared module would be better.
  # For this example I'll just duplicate or call it if I can.
  # But since I can't easily call private methods from another controller, I'll duplicate for now
  # as this is a small prototype.
  
  defp build_for_view(:index, store, filters) do
    agg_events = Events.aggregate_event_counts(store.events, filters)
    figure = TimeSeries.build_figure(agg_events)
    {figure, %{total_events: figure.meta.total_count}}
  end

  defp build_for_view(:trends, store, filters) do
    agg = Events.aggregate_event_counts(store.events, filters)
    figure = TimeSeries.build_figure(agg)
    {figure, %{total_events: figure.meta.total_count}}
  end

  defp build_for_view(:services, store, filters) do
    agg = Services.aggregate_service_error_rates(store.events, store.services, filters)
    figure = ServiceBar.build_figure(agg)
    {figure, %{avg_error_rate: if(length(agg.error_rates) > 0, do: Enum.sum(agg.error_rates) / length(agg.error_rates), else: 0.0)}}
  end

  defp build_for_view(:distributions, store, filters) do
    agg = Distributions.aggregate_latency_histogram(store.latency_samples, filters)
    figure = LatencyHistogram.build_figure(agg)
    {figure, %{p50: agg.p50, p95: agg.p95, p99: agg.p99}}
  end

  defp build_for_view(:heatmap, store, filters) do
    agg = Heatmap.aggregate_event_heatmap(store.events, filters)
    figure = HeatmapChart.build_figure(agg)
    {figure, %{total_events: Enum.sum(List.flatten(agg.counts))}}
  end

  defp build_for_view(:funnel, store, filters) do
    agg = Funnel.aggregate_funnel_stages(store.sessions, filters)
    figure = FunnelChart.build_figure(agg)
    {figure, %{conversion_rate: if(List.first(agg.counts, 0) > 0, do: List.last(agg.counts, 0) / List.first(agg.counts), else: 0.0)}}
  end

  defp build_for_view(:incidents, store, filters) do
    agg = Incidents.aggregate_incident_severity(store.incidents, filters)
    figure = IncidentBar.build_figure(agg)
    {figure, %{total_incidents: Enum.sum(agg.counts)}}
  end
end
