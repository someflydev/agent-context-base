package models

// WorkspaceConfig defines a workspace with its sync configuration.
// @Description Workspace configuration object
// WorkspaceConfig godoc
type WorkspaceConfig struct {
	// The workspace's globally unique identifier.
	// @example "550e8400-e29b-41d4-a716-446655440001"
	ID string `json:"id"`
	// Human-friendly workspace name.
	// @example "Acme Workspace"
	Name string `json:"name"`
	// Lowercase slug used in URLs.
	// @example "acme-workspace"
	Slug string `json:"slug"`
	// Email address for the primary owner.
	// @example "admin@acme.example.com"
	OwnerEmail string `json:"owner_email"`
	// Billing plan selector.
	// @example "pro"
	Plan string `json:"plan"`
	// Maximum sync runs allowed in the configured plan.
	// @example 50
	MaxSyncRuns int `json:"max_sync_runs"`
}
