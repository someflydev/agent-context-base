package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/santhosh-tekuri/jsonschema/v5"
)

func workspaceConfigSchema() map[string]interface{} {
	return map[string]interface{}{
		"$schema":              "https://json-schema.org/draft/2020-12/schema",
		"$id":                  "https://example.com/workspace_config.schema.json",
		"$comment":             "Generated for the WorkspaceSyncContext domain. Go openapi-generation Lane B example. Validate against domain/fixtures/valid/ and domain/fixtures/invalid/.",
		"title":                "WorkspaceConfig",
		"type":                 "object",
		"additionalProperties": false,
		"properties": map[string]interface{}{
			"id":            map[string]interface{}{"type": "string", "format": "uuid"},
			"name":          map[string]interface{}{"type": "string", "minLength": 3, "maxLength": 100},
			"slug":          map[string]interface{}{"type": "string", "pattern": "^[a-z][a-z0-9-]{1,48}[a-z0-9]$"},
			"owner_email":   map[string]interface{}{"type": "string", "format": "email"},
			"plan":          map[string]interface{}{"type": "string", "enum": []string{"free", "pro", "enterprise"}},
			"max_sync_runs": map[string]interface{}{"type": "integer", "minimum": 1, "maximum": 1000},
			"settings": map[string]interface{}{
				"type":                 "object",
				"additionalProperties": false,
				"properties": map[string]interface{}{
					"retry_max":         map[string]interface{}{"type": "integer", "minimum": 0, "maximum": 10},
					"timeout_seconds":   map[string]interface{}{"type": "integer", "minimum": 10, "maximum": 3600},
					"notify_on_failure": map[string]interface{}{"type": "boolean"},
					"webhook_url": map[string]interface{}{
						"anyOf": []interface{}{
							map[string]interface{}{"type": "string", "format": "uri"},
							map[string]interface{}{"type": "null"},
						},
					},
				},
				"required": []string{"retry_max", "timeout_seconds", "notify_on_failure", "webhook_url"},
			},
			"tags": map[string]interface{}{
				"type":     "array",
				"maxItems": 20,
				"items":    map[string]interface{}{"type": "string", "minLength": 1, "maxLength": 50},
			},
			"created_at": map[string]interface{}{"type": "string", "format": "date-time"},
			"suspended_until": map[string]interface{}{
				"anyOf": []interface{}{
					map[string]interface{}{"type": "string", "format": "date-time"},
					map[string]interface{}{"type": "null"},
				},
			},
		},
		"required": []string{
			"id", "name", "slug", "owner_email", "plan", "max_sync_runs",
			"settings", "tags", "created_at", "suspended_until",
		},
	}
}

func exportSchema() ([]byte, error) {
	schema := workspaceConfigSchema()
	return json.MarshalIndent(schema, "", "  ")
}

func driftCheck() error {
	compiler := jsonschema.NewCompiler()
	schemaPath := filepath.Join(".", "workspace_config.schema.json")
	schemaBytes, err := os.ReadFile(schemaPath)
	if err != nil {
		return err
	}
	if err := compiler.AddResource(schemaPath, strings.NewReader(string(schemaBytes))); err != nil {
		return err
	}
	compiled, err := compiler.Compile(schemaPath)
	if err != nil {
		return err
	}
	cases := []struct {
		name   string
		path   string
		expect bool
	}{
		{"valid", filepath.Join("..", "..", "domain", "fixtures", "valid", "workspace_config_full.json"), true},
		{"invalid", filepath.Join("..", "..", "domain", "fixtures", "invalid", "workspace_config_bad_slug.json"), false},
	}
	for _, tc := range cases {
		data, err := os.ReadFile(tc.path)
		if err != nil {
			return err
		}
		var value interface{}
		if err := json.Unmarshal(data, &value); err != nil {
			return err
		}
		err = compiled.Validate(value)
		if tc.expect && err != nil {
			return fmt.Errorf("%s fixture failed drift check: %w", tc.name, err)
		}
		if !tc.expect && err == nil {
			return fmt.Errorf("%s fixture unexpectedly passed drift check", tc.name)
		}
	}
	return nil
}

func main() {
	payload, err := exportSchema()
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile("workspace_config.schema.json", payload, 0o644); err != nil {
		panic(err)
	}
	if err := driftCheck(); err != nil {
		panic(err)
	}
	fmt.Println("schema export and drift checks passed")
}
