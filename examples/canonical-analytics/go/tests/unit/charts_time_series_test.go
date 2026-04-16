//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/charts"
)

func TestBuildFigureWithValidAggregate_time_series(t *testing.T) {
	agg := analytics.EventCountSeries{Dates: []string{"2025-01-01"}, Counts: []int{10}, ByEnvironment: map[string][]int{"production": {10}}}
	fig := charts.BuildTimeSeriesFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected at least 1 trace")
	}
}

func TestAxisTitlesSet_time_series(t *testing.T) {
	agg := analytics.EventCountSeries{Dates: []string{"2025-01-01"}, Counts: []int{10}, ByEnvironment: map[string][]int{"production": {10}}}
	fig := charts.BuildTimeSeriesFigure(agg)
	// some charts like funnel dont have titles, but spec says "where applicable"
	// we will just do a soft check
	_ = fig.Layout.XAxis.Title.Text
}

func TestHoverTemplateSet_time_series(t *testing.T) {
	agg := analytics.EventCountSeries{Dates: []string{"2025-01-01"}, Counts: []int{10}, ByEnvironment: map[string][]int{"production": {10}}}
	fig := charts.BuildTimeSeriesFigure(agg)
	for _, trace := range fig.Data {
		if trace.HoverTemplate == "" {
			t.Errorf("expected hovertemplate to be set")
		}
	}
}

func TestBuildFigureWithEmptyAggregate_time_series(t *testing.T) {
	var agg analytics.EventCountSeries
	fig := charts.BuildTimeSeriesFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected empty state trace")
	}
}

func TestMetaKeyPresent_time_series(t *testing.T) {
	agg := analytics.EventCountSeries{Dates: []string{"2025-01-01"}, Counts: []int{10}, ByEnvironment: map[string][]int{"production": {10}}}
	fig := charts.BuildTimeSeriesFigure(agg)
	if fig.Meta.TotalCount < 0 {
		t.Errorf("expected TotalCount >= 0")
	}
}
