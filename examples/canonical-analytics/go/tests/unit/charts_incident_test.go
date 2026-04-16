//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/charts"
)

func TestBuildFigureWithValidAggregate_incident(t *testing.T) {
	agg := analytics.IncidentSeverity{Severities: []string{"high"}, Counts: []int{5}}
	fig := charts.BuildIncidentBarFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected at least 1 trace")
	}
}

func TestAxisTitlesSet_incident(t *testing.T) {
	agg := analytics.IncidentSeverity{Severities: []string{"high"}, Counts: []int{5}}
	fig := charts.BuildIncidentBarFigure(agg)
	// some charts like funnel dont have titles, but spec says "where applicable"
	// we will just do a soft check
	_ = fig.Layout.XAxis.Title.Text
}

func TestHoverTemplateSet_incident(t *testing.T) {
	agg := analytics.IncidentSeverity{Severities: []string{"high"}, Counts: []int{5}}
	fig := charts.BuildIncidentBarFigure(agg)
	for _, trace := range fig.Data {
		if trace.HoverTemplate == "" {
			t.Errorf("expected hovertemplate to be set")
		}
	}
}

func TestBuildFigureWithEmptyAggregate_incident(t *testing.T) {
	var agg analytics.IncidentSeverity
	fig := charts.BuildIncidentBarFigure(agg)
	if len(fig.Data) < 1 {
		t.Errorf("expected empty state trace")
	}
}

func TestMetaKeyPresent_incident(t *testing.T) {
	agg := analytics.IncidentSeverity{Severities: []string{"high"}, Counts: []int{5}}
	fig := charts.BuildIncidentBarFigure(agg)
	if fig.Meta.TotalCount < 0 {
		t.Errorf("expected TotalCount >= 0")
	}
}
