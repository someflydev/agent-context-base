//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)


func TestWithSmokeFixture_heatmap(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{}
	res := analytics.AggregateHeatmap(store. Events, f)
	if len(res.Hours) == 0 {
		t.Errorf("expected non-zero result")
	}
}

func TestWithEmptyInput_heatmap(t *testing.T) {
	f := filters.FilterState{}
	// should not panic
	analytics.AggregateHeatmap([]data.Event{}, f)
}

func TestFilterByService_heatmap(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Services: []string{"billing-api"}}
	analytics.AggregateHeatmap(store.Events, f)
}

func TestFilterByEnvironment_heatmap(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Environment: []string{"production"}}
	analytics.AggregateHeatmap(store.Events, f)
}
