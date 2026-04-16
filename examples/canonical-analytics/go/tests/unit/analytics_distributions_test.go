//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)


func TestWithSmokeFixture_distributions(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{}
	res := analytics.AggregateLatencyHistogram(store. LatencySamples, store.Services, f)
	if len(res.Values) == 0 {
		t.Errorf("expected non-zero result")
	}
}

func TestWithEmptyInput_distributions(t *testing.T) {
	f := filters.FilterState{}
	// should not panic
	analytics.AggregateLatencyHistogram([]data.LatencySample{}, nil, f)
}

func TestFilterByService_distributions(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Services: []string{"billing-api"}}
	analytics.AggregateLatencyHistogram(store.LatencySamples, store.Services, f)
}

func TestFilterByEnvironment_distributions(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Environment: []string{"production"}}
	analytics.AggregateLatencyHistogram(store.LatencySamples, store.Services, f)
}
