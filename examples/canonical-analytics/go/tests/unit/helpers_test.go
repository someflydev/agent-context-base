//go:build unit

package unit

import (
	"testing"

	"analytics-workbench-go/internal/data"
)

func getStore(t *testing.T) *data.FixtureStore {
	store, err := data.ReadFixtures(data.GetFixturePath())
	if err != nil {
		t.Fatalf("failed to load fixtures: %v", err)
	}
	return store
}
