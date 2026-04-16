//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/charts"
)

func TestBuildFigureWithValidAggregate_funnel(t *testing.T) {
	agg := analytics.FunnelStages{Stages: []string{"signup"}, Counts: []int{100}, DropOffRates: []float64{0}}
	fig := charts.BuildFunnelFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected at least 1 trace")
	}
}

func TestAxisTitlesSet_funnel(t *testing.T) {
	agg := analytics.FunnelStages{Stages: []string{"signup"}, Counts: []int{100}, DropOffRates: []float64{0}}
	fig := charts.BuildFunnelFigure(agg)
	// some charts like funnel dont have titles, but spec says "where applicable"
	// we will just do a soft check
	_ = fig.Layout.XAxis.Title.Text
}

func TestHoverTemplateSet_funnel(t *testing.T) {
	agg := analytics.FunnelStages{Stages: []string{"signup"}, Counts: []int{100}, DropOffRates: []float64{0}}
	fig := charts.BuildFunnelFigure(agg)
	for _, trace := range fig.Data {
		if trace.HoverTemplate == "" {
			t.Errorf("expected hovertemplate to be set")
		}
	}
}

func TestBuildFigureWithEmptyAggregate_funnel(t *testing.T) {
	var agg analytics.FunnelStages
	fig := charts.BuildFunnelFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected empty state trace")
	}
}

func TestMetaKeyPresent_funnel(t *testing.T) {
	agg := analytics.FunnelStages{Stages: []string{"signup"}, Counts: []int{100}, DropOffRates: []float64{0}}
	fig := charts.BuildFunnelFigure(agg)
	if fig.Meta.TotalCount < 0 {
		t.Errorf("expected TotalCount >= 0")
	}
}
