package data

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
)

type FixtureStore struct {
	Events         []Event         `json:"events"`
	Sessions       []Session       `json:"sessions"`
	Services       []Service       `json:"services"`
	Deployments    []Deployment    `json:"deployments"`
	Incidents      []Incident      `json:"incidents"`
	LatencySamples []LatencySample `json:"latency_samples"`
	FunnelStages   []FunnelStage   `json:"funnel_stages"`
}

// GetFixturePath resolves the fixture path relative to go.mod, supports FIXTURE_PATH env var.
// (path must resolve to examples/canonical-analytics/domain/fixtures/smoke.json)
func GetFixturePath() string {
	envPath := os.Getenv("FIXTURE_PATH")
	if envPath != "" {
		return envPath
	}

	// Default fallback using runtime caller info to get to repo root
	_, b, _, _ := runtime.Caller(0)
	// from examples/canonical-analytics/go/internal/data/loader.go -> repo root is 5 levels up
	repoRoot := filepath.Join(filepath.Dir(b), "../../../../../")
	return filepath.Join(repoRoot, "examples/canonical-analytics/domain/fixtures/smoke.json")
}

func ReadFixtures(path string) (*FixtureStore, error) {
	bytes, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read fixture file %s: %w", path, err)
	}

	var store FixtureStore
	if err := json.Unmarshal(bytes, &store); err != nil {
		return nil, fmt.Errorf("failed to parse fixture json: %w", err)
	}

	return &store, nil
}
