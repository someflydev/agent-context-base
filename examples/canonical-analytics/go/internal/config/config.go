package config

import "os"

type Config struct {
	FixturePath string
	Port        string
	Debug       bool
}

func Load() Config {
	fixturePath := os.Getenv("FIXTURE_PATH")
	if fixturePath == "" {
		fixturePath = "examples/canonical-analytics/domain/fixtures/smoke.json"
	}
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	debug := os.Getenv("DEBUG") == "true"

	return Config{
		FixturePath: fixturePath,
		Port:        port,
		Debug:       debug,
	}
}
