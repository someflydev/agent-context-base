//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)


func TestWithSmokeFixture_services(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{}
	res := analytics.AggregateServices(store. Events, store.Services, f)
	if len(res.Services) == 0 {
		t.Errorf("expected non-zero result")
	}
}

func TestWithEmptyInput_services(t *testing.T) {
	f := filters.FilterState{}
	// should not panic
	analytics.AggregateServices([]data.Event{}, nil, f)
}

func TestFilterByService_services(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Services: []string{"billing-api"}}
	analytics.AggregateServices(store.Events, store.Services, f)
}

func TestFilterByEnvironment_services(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Environment: []string{"production"}}
	analytics.AggregateServices(store.Events, store.Services, f)
}
