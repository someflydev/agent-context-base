//go:build unit

package unit

import (
	"testing"
	"analytics-workbench-go/internal/analytics"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/filters"
)


func TestWithSmokeFixture_funnel(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{}
	res := analytics.AggregateFunnel(store. Sessions, store.FunnelStages, f)
	if len(res.Stages) == 0 {
		t.Errorf("expected non-zero result")
	}
}

func TestWithEmptyInput_funnel(t *testing.T) {
	f := filters.FilterState{}
	// should not panic
	analytics.AggregateFunnel([]data.Session{}, nil, f)
}

func TestFilterByService_funnel(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Services: []string{"billing-api"}}
	analytics.AggregateFunnel(store.Sessions, store.FunnelStages, f)
}

func TestFilterByEnvironment_funnel(t *testing.T) {
	store := getStore(t)
	f := filters.FilterState{Environment: []string{"production"}}
	analytics.AggregateFunnel(store.Sessions, store.FunnelStages, f)
}
