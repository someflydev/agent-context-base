defmodule AnalyticsWorkbenchWeb.PageController do
  use AnalyticsWorkbenchWeb, :controller

  alias AnalyticsWorkbench.Data.Store
  alias AnalyticsWorkbench.Filters
  alias AnalyticsWorkbench.Analytics.{Events, Services, Distributions, Heatmap, Funnel, Incidents}
  alias AnalyticsWorkbench.Charts.{TimeSeries, ServiceBar, LatencyHistogram, HeatmapChart, FunnelChart, IncidentBar}

  def index(conn, params), do: render_view(conn, :index, params)
  def trends(conn, params), do: render_view(conn, :trends, params)
  def services(conn, params), do: render_view(conn, :services, params)
  def distributions(conn, params), do: render_view(conn, :distributions, params)
  def heatmap(conn, params), do: render_view(conn, :heatmap, params)
  def funnel(conn, params), do: render_view(conn, :funnel, params)
  def incidents(conn, params), do: render_view(conn, :incidents, params)

  defp render_view(conn, view, params) do
    filters = Filters.parse(params)
    store = Store.get()
    {figure, summary} = build_for_view(view, store, filters)
    figure_json = Jason.encode!(figure)
    
    render(conn, "#{view}.html",
      figure_json: figure_json,
      summary: summary,
      filters: filters,
      services_list: Enum.map(store.services, & &1.name) |> Enum.uniq() |> Enum.sort(),
      environment_list: ["production", "staging", "development"],
      severity_list: ["sev1", "sev2", "sev3"],
      view_name: to_string(view)
    )
  end

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
