//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)


func TestWithSmokeFixture_incidents(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{}
	res := analytics.AggregateIncidents(store. Incidents, store.Services, f)
	if len(res.Severities) == 0 {
		t.Errorf("expected non-zero result")
	}
}

func TestWithEmptyInput_incidents(t *testing.T) {
	f := filters.FilterState{}
	// should not panic
	analytics.AggregateIncidents([]data.Incident{}, nil, f)
}

func TestFilterByService_incidents(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Services: []string{"billing-api"}}
	analytics.AggregateIncidents(store.Incidents, store.Services, f)
}

func TestFilterByEnvironment_incidents(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Environment: []string{"production"}}
	analytics.AggregateIncidents(store.Incidents, store.Services, f)
}
