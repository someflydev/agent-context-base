package core

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
)

func ResolveFixturesPath(override string) string {
	if override != "" {
		return override
	}
	if env := os.Getenv("TASKFLOW_FIXTURES_PATH"); env != "" {
		return env
	}
	return filepath.Clean(filepath.Join("..", "fixtures"))
}

func loadJSON(path string, name string, target any) error {
	if _, err := os.Stat(path); err != nil {
		return fmt.Errorf("fixtures path does not exist: %s", path)
	}
	payload, err := os.ReadFile(filepath.Join(path, name))
	if err != nil {
		return fmt.Errorf("missing fixture file: %s", filepath.Join(path, name))
	}
	if err := json.Unmarshal(payload, target); err != nil {
		return fmt.Errorf("failed to parse %s: %w", filepath.Join(path, name), err)
	}
	return nil
}

func LoadJobs(path string) ([]Job, error) {
	var jobs []Job
	return jobs, loadJSON(path, "jobs.json", &jobs)
}

func LoadEvents(path string) ([]Event, error) {
	var events []Event
	if err := loadJSON(path, "events.json", &events); err != nil {
		return nil, err
	}
	sort.Slice(events, func(i, j int) bool {
		return events[i].Timestamp < events[j].Timestamp
	})
	return events, nil
}

func LoadConfig(path string) (Config, error) {
	var config Config
	return config, loadJSON(path, "config.json", &config)
}
