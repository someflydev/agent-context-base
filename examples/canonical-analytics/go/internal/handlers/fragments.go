package handlers

import (
	"context"
	"net/http"
	"strings"

	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/charts"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
	"analytics-workbench-go/internal/views"

	"github.com/labstack/echo/v4"
)

func ChartFragmentHandler(c echo.Context) error {
	view := c.QueryParam("view")
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	var figJSON string
	var figJSONBox string

	switch strings.ToLower(view) {
	case "overview", "trends":
		agg := analytics.AggregateEvents(store.Events, f)
		fig := charts.BuildTimeSeriesFigure(agg)
		b, _ := fig.ToJSON()
		figJSON = string(b)
	case "services":
		agg := analytics.AggregateServices(store.Events, store.Services, f)
		fig := charts.BuildServiceBarFigure(agg)
		b, _ := fig.ToJSON()
		figJSON = string(b)
	case "distributions":
		aggHist := analytics.AggregateLatencyHistogram(store.LatencySamples, store.Services, f)
		figHist := charts.BuildLatencyHistogramFigure(aggHist)
		bHist, _ := figHist.ToJSON()
		figJSON = string(bHist)

		aggBox := analytics.AggregateLatencyByService(store.LatencySamples, store.Services, f)
		figBox := charts.BuildLatencyBoxplotFigure(aggBox)
		bBox, _ := figBox.ToJSON()
		figJSONBox = string(bBox)
	case "heatmap":
		agg := analytics.AggregateHeatmap(store.Events, f)
		fig := charts.BuildHeatmapFigure(agg)
		b, _ := fig.ToJSON()
		figJSON = string(b)
	case "funnel":
		agg := analytics.AggregateFunnel(store.Sessions, store.FunnelStages, f)
		fig := charts.BuildFunnelFigure(agg)
		b, _ := fig.ToJSON()
		figJSON = string(b)
	case "incidents":
		agg := analytics.AggregateIncidents(store.Incidents, store.Services, f)
		fig := charts.BuildIncidentBarFigure(agg)
		b, _ := fig.ToJSON()
		figJSON = string(b)
	default:
		return c.String(http.StatusBadRequest, "Unknown view")
	}

	c.Response().Header().Set(echo.HeaderContentType, echo.MIMETextHTML)
	if strings.ToLower(view) == "distributions" {
		return views.ChartPair(figJSON, figJSONBox).Render(context.Background(), c.Response().Writer)
	}
	return views.Chart(figJSON).Render(context.Background(), c.Response().Writer)
}

func SummaryFragmentHandler(c echo.Context) error {
	view := c.QueryParam("view")
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	var summary any

	switch strings.ToLower(view) {
	case "overview", "trends":
		agg := analytics.AggregateEvents(store.Events, f)
		fig := charts.BuildTimeSeriesFigure(agg)
		summary = map[string]interface{}{
			"Total Events": fig.Meta.TotalCount,
			"Date Range":   fig.Meta.FiltersApplied,
		}
	case "services":
		agg := analytics.AggregateServices(store.Events, store.Services, f)
		fig := charts.BuildServiceBarFigure(agg)
		summary = map[string]interface{}{
			"Total Events": fig.Meta.TotalCount,
		}
	case "distributions":
		aggHist := analytics.AggregateLatencyHistogram(store.LatencySamples, store.Services, f)
		summary = map[string]interface{}{
			"P50": aggHist.P50,
			"P95": aggHist.P95,
			"P99": aggHist.P99,
		}
	case "heatmap":
		agg := analytics.AggregateHeatmap(store.Events, f)
		fig := charts.BuildHeatmapFigure(agg)
		summary = map[string]interface{}{
			"Total Density": fig.Meta.TotalCount,
		}
	case "funnel":
		agg := analytics.AggregateFunnel(store.Sessions, store.FunnelStages, f)
		fig := charts.BuildFunnelFigure(agg)
		summary = map[string]interface{}{
			"Total Sessions": fig.Meta.TotalCount,
		}
	case "incidents":
		agg := analytics.AggregateIncidents(store.Incidents, store.Services, f)
		summary = map[string]interface{}{
			"MTTR By Severity": agg.MTTRBySeverity,
		}
	default:
		return c.String(http.StatusBadRequest, "Unknown view")
	}

	c.Response().Header().Set(echo.HeaderContentType, echo.MIMETextHTML)
	return views.Summary(summary).Render(context.Background(), c.Response().Writer)
}

func DetailsFragmentHandler(c echo.Context) error {
	view := c.QueryParam("view")
	if strings.ToLower(view) != "services" {
		return c.String(http.StatusOK, "")
	}

	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)
	serviceName := c.QueryParam("service")

	// Just show top incidents for this service or something
	var matched []data.Incident
	for _, i := range store.Incidents {
		if serviceName != "" && i.Service != serviceName {
			continue
		}
		if !f.ContainsEnvironment(i.Environment) {
			continue
		}
		if !f.ContainsSeverity(i.Severity) {
			continue
		}
		matched = append(matched, i)
	}

	// Limit to top 5
	if len(matched) > 5 {
		matched = matched[:5]
	}

	c.Response().Header().Set(echo.HeaderContentType, echo.MIMETextHTML)
	return views.Details(matched).Render(context.Background(), c.Response().Writer)
}
