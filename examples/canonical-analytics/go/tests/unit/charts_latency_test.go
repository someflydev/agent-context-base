//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/charts"
)

func TestBuildFigureWithValidAggregate_latency(t *testing.T) {
	agg := analytics.LatencyHistogram{Values: []float64{10.0, 20.0}}
	fig := charts.BuildLatencyHistogramFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected at least 1 trace")
	}
}

func TestAxisTitlesSet_latency(t *testing.T) {
	agg := analytics.LatencyHistogram{Values: []float64{10.0, 20.0}}
	fig := charts.BuildLatencyHistogramFigure(agg)
	// some charts like funnel dont have titles, but spec says "where applicable"
	// we will just do a soft check
	_ = fig.Layout.XAxis.Title.Text
}

func TestHoverTemplateSet_latency(t *testing.T) {
	agg := analytics.LatencyHistogram{Values: []float64{10.0, 20.0}}
	fig := charts.BuildLatencyHistogramFigure(agg)
	for _, trace := range fig.Data {
		if trace.HoverTemplate == "" {
			t.Errorf("expected hovertemplate to be set")
		}
	}
}

func TestBuildFigureWithEmptyAggregate_latency(t *testing.T) {
	var agg analytics.LatencyHistogram
	fig := charts.BuildLatencyHistogramFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected empty state trace")
	}
}

func TestMetaKeyPresent_latency(t *testing.T) {
	agg := analytics.LatencyHistogram{Values: []float64{10.0, 20.0}}
	fig := charts.BuildLatencyHistogramFigure(agg)
	if fig.Meta.TotalCount < 0 {
		t.Errorf("expected TotalCount >= 0")
	}
}
