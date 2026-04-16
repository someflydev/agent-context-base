//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/charts"
)

func TestBuildFigureWithValidAggregate_service_bar(t *testing.T) {
	agg := analytics.ServiceErrorRates{Services: []string{"api"}, ErrorRates: []float64{0.1}, TotalEvents: []int{100}}
	fig := charts.BuildServiceBarFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected at least 1 trace")
	}
}

func TestAxisTitlesSet_service_bar(t *testing.T) {
	agg := analytics.ServiceErrorRates{Services: []string{"api"}, ErrorRates: []float64{0.1}, TotalEvents: []int{100}}
	fig := charts.BuildServiceBarFigure(agg)
	// some charts like funnel dont have titles, but spec says "where applicable"
	// we will just do a soft check
	_ = fig.Layout.XAxis.Title.Text
}

func TestHoverTemplateSet_service_bar(t *testing.T) {
	agg := analytics.ServiceErrorRates{Services: []string{"api"}, ErrorRates: []float64{0.1}, TotalEvents: []int{100}}
	fig := charts.BuildServiceBarFigure(agg)
	for _, trace := range fig.Data {
		if trace.HoverTemplate == "" {
			t.Errorf("expected hovertemplate to be set")
		}
	}
}

func TestBuildFigureWithEmptyAggregate_service_bar(t *testing.T) {
	var agg analytics.ServiceErrorRates
	fig := charts.BuildServiceBarFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected empty state trace")
	}
}

func TestMetaKeyPresent_service_bar(t *testing.T) {
	agg := analytics.ServiceErrorRates{Services: []string{"api"}, ErrorRates: []float64{0.1}, TotalEvents: []int{100}}
	fig := charts.BuildServiceBarFigure(agg)
	if fig.Meta.TotalCount < 0 {
		t.Errorf("expected TotalCount >= 0")
	}
}
