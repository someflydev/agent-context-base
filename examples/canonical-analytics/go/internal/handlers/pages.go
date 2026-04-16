package handlers

import (
	"context"
	"sort"

	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/charts"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
	"analytics-workbench-go/internal/views"

	"github.com/labstack/echo/v4"
)

func buildCommonTemplateData(c echo.Context, viewName string) views.TemplateData {
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	var srvOptions []views.SelectOption
	var envOptions []views.SelectOption
	var sevOptions []views.SelectOption

	// unique services
	srvMap := make(map[string]bool)
	for _, s := range store.Services {
		if !srvMap[s.Name] {
			srvMap[s.Name] = true
			srvOptions = append(srvOptions, views.SelectOption{
				Value:    s.Name,
				Label:    s.Name,
				Selected: f.ContainsService(s.Name) && len(f.Services) > 0,
			})
		}
	}
	sort.Slice(srvOptions, func(i, j int) bool { return srvOptions[i].Label < srvOptions[j].Label })

	// environments
	envs := []string{"production", "staging", "development"}
	for _, e := range envs {
		envOptions = append(envOptions, views.SelectOption{
			Value:    e,
			Label:    e,
			Selected: f.ContainsEnvironment(e) && len(f.Environment) > 0,
		})
	}

	// severity
	sevs := []string{"sev1", "sev2", "sev3", "sev4"}
	for _, s := range sevs {
		sevOptions = append(sevOptions, views.SelectOption{
			Value:    s,
			Label:    s,
			Selected: f.ContainsSeverity(s) && len(f.Severity) > 0,
		})
	}

	return views.TemplateData{
		ViewName:         viewName,
		ActiveFilters:    f,
		ServicesList:     srvOptions,
		EnvironmentsList: envOptions,
		SeverityList:     sevOptions,
	}
}

func renderPage(c echo.Context, data views.TemplateData) error {
	c.Response().Header().Set(echo.HeaderContentType, echo.MIMETextHTML)
	return views.PageTemplate(data).Render(context.Background(), c.Response().Writer)
}

func OverviewPageHandler(c echo.Context) error {
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	agg := analytics.AggregateEvents(store.Events, f)
	fig := charts.BuildTimeSeriesFigure(agg)
	jsonBytes, _ := fig.ToJSON()

	data := buildCommonTemplateData(c, "Overview")
	data.FigureJSON = string(jsonBytes)
	data.Summary = map[string]interface{}{
		"Total Events": fig.Meta.TotalCount,
	}

	return renderPage(c, data)
}

func TrendsPageHandler(c echo.Context) error {
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	agg := analytics.AggregateEvents(store.Events, f)
	fig := charts.BuildTimeSeriesFigure(agg)
	jsonBytes, _ := fig.ToJSON()

	data := buildCommonTemplateData(c, "Trends")
	data.FigureJSON = string(jsonBytes)
	data.Summary = map[string]interface{}{
		"Total Events": fig.Meta.TotalCount,
		"Date Range":   fig.Meta.FiltersApplied, // simplified
	}

	return renderPage(c, data)
}

func ServicesPageHandler(c echo.Context) error {
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	agg := analytics.AggregateServices(store.Events, store.Services, f)
	fig := charts.BuildServiceBarFigure(agg)
	jsonBytes, _ := fig.ToJSON()

	data := buildCommonTemplateData(c, "Services")
	data.FigureJSON = string(jsonBytes)
	data.Summary = map[string]interface{}{
		"Total Events": fig.Meta.TotalCount,
	}

	return renderPage(c, data)
}

func DistributionsPageHandler(c echo.Context) error {
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	aggHist := analytics.AggregateLatencyHistogram(store.LatencySamples, store.Services, f)
	figHist := charts.BuildLatencyHistogramFigure(aggHist)
	jsonBytesHist, _ := figHist.ToJSON()

	aggBox := analytics.AggregateLatencyByService(store.LatencySamples, store.Services, f)
	figBox := charts.BuildLatencyBoxplotFigure(aggBox)
	jsonBytesBox, _ := figBox.ToJSON()

	data := buildCommonTemplateData(c, "Distributions")
	data.FigureJSON = string(jsonBytesHist)
	data.FigureJSONBox = string(jsonBytesBox)
	data.Summary = map[string]interface{}{
		"P50": aggHist.P50,
		"P95": aggHist.P95,
		"P99": aggHist.P99,
	}

	return renderPage(c, data)
}

func HeatmapPageHandler(c echo.Context) error {
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	agg := analytics.AggregateHeatmap(store.Events, f)
	fig := charts.BuildHeatmapFigure(agg)
	jsonBytes, _ := fig.ToJSON()

	data := buildCommonTemplateData(c, "Heatmap")
	data.FigureJSON = string(jsonBytes)
	data.Summary = map[string]interface{}{
		"Total Density": fig.Meta.TotalCount,
	}

	return renderPage(c, data)
}

func FunnelPageHandler(c echo.Context) error {
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	agg := analytics.AggregateFunnel(store.Sessions, store.FunnelStages, f)
	fig := charts.BuildFunnelFigure(agg)
	jsonBytes, _ := fig.ToJSON()

	data := buildCommonTemplateData(c, "Funnel")
	data.FigureJSON = string(jsonBytes)
	data.Summary = map[string]interface{}{
		"Total Sessions": fig.Meta.TotalCount,
	}

	return renderPage(c, data)
}

func IncidentsPageHandler(c echo.Context) error {
	store := c.Get("store").(*data.FixtureStore)
	f := filters.ParseFilterState(c)

	agg := analytics.AggregateIncidents(store.Incidents, store.Services, f)
	fig := charts.BuildIncidentBarFigure(agg)
	jsonBytes, _ := fig.ToJSON()

	data := buildCommonTemplateData(c, "Incidents")
	data.FigureJSON = string(jsonBytes)
	data.Summary = map[string]interface{}{
		"MTTR By Severity": agg.MTTRBySeverity,
	}

	return renderPage(c, data)
}
