//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)


func TestWithSmokeFixture_events(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{}
	res := analytics.AggregateEvents(store. Events, f)
	if len(res.Dates) == 0 {
		t.Errorf("expected non-zero result")
	}
}

func TestWithEmptyInput_events(t *testing.T) {
	f := filters.FilterState{}
	// should not panic
	analytics.AggregateEvents([]data.Event{}, f)
}

func TestFilterByService_events(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Services: []string{"billing-api"}}
	analytics.AggregateEvents(store.Events, f)
}

func TestFilterByEnvironment_events(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Environment: []string{"production"}}
	analytics.AggregateEvents(store.Events, f)
}
