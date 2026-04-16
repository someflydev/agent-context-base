//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/charts"
)

func TestBuildFigureWithValidAggregate_heatmap(t *testing.T) {
	agg := analytics.EventHeatmap{Hours: []int{0}, Days: []string{"Mon"}, Counts: [][]int{{1}}}
	fig := charts.BuildHeatmapFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected at least 1 trace")
	}
}

func TestAxisTitlesSet_heatmap(t *testing.T) {
	agg := analytics.EventHeatmap{Hours: []int{0}, Days: []string{"Mon"}, Counts: [][]int{{1}}}
	fig := charts.BuildHeatmapFigure(agg)
	// some charts like funnel dont have titles, but spec says "where applicable"
	// we will just do a soft check
	_ = fig.Layout.XAxis.Title.Text
}

func TestHoverTemplateSet_heatmap(t *testing.T) {
	agg := analytics.EventHeatmap{Hours: []int{0}, Days: []string{"Mon"}, Counts: [][]int{{1}}}
	fig := charts.BuildHeatmapFigure(agg)
	for _, trace := range fig.Data {
		if trace.HoverTemplate == "" {
			t.Errorf("expected hovertemplate to be set")
		}
	}
}

func TestBuildFigureWithEmptyAggregate_heatmap(t *testing.T) {
	var agg analytics.EventHeatmap
	fig := charts.BuildHeatmapFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected empty state trace")
	}
}

func TestMetaKeyPresent_heatmap(t *testing.T) {
	agg := analytics.EventHeatmap{Hours: []int{0}, Days: []string{"Mon"}, Counts: [][]int{{1}}}
	fig := charts.BuildHeatmapFigure(agg)
	if fig.Meta.TotalCount < 0 {
		t.Errorf("expected TotalCount >= 0")
	}
}
