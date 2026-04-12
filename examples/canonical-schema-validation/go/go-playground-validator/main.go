package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"workspace-sync-validator-go-playground/models"
	"workspace-sync-validator-go-playground/validate"
)

func loadFixture(name string) (*models.WorkspaceConfig, error) {
	path := filepath.Join("..", "..", "domain", "fixtures", name)
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var cfg models.WorkspaceConfig
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}

func main() {
	fixtures := []string{
		"valid/workspace_config_basic.json",
		"invalid/workspace_config_bad_slug.json",
	}
	for _, fixture := range fixtures {
		cfg, err := loadFixture(fixture)
		if err != nil {
			fmt.Printf("%s FAIL: %v\n", fixture, err)
			continue
		}
		if err := validate.ValidateWorkspaceConfig(cfg); err != nil {
			fmt.Printf("%s FAIL: %v\n", fixture, err)
			continue
		}
		fmt.Printf("%s PASS\n", fixture)
	}
}
