package models

import (
	"encoding/json"
	"time"
)

type PlanType string

const (
	PlanFree       PlanType = "free"
	PlanPro        PlanType = "pro"
	PlanEnterprise PlanType = "enterprise"
)

type SyncStatus string

const (
	SyncPending   SyncStatus = "pending"
	SyncRunning   SyncStatus = "running"
	SyncSucceeded SyncStatus = "succeeded"
	SyncFailed    SyncStatus = "failed"
	SyncCancelled SyncStatus = "cancelled"
)

type TriggerType string

const (
	TriggerManual    TriggerType = "manual"
	TriggerScheduled TriggerType = "scheduled"
	TriggerWebhook   TriggerType = "webhook"
)

type WebhookEventType string

const (
	WebhookSyncCompleted    WebhookEventType = "sync.completed"
	WebhookSyncFailed       WebhookEventType = "sync.failed"
	WebhookWorkspaceStopped WebhookEventType = "workspace.suspended"
)

type SourceType string

const (
	SourceHTTPPoll   SourceType = "http_poll"
	SourceWebhook    SourceType = "webhook_push"
	SourceFileWatch  SourceType = "file_watch"
	SourceDatabaseCD SourceType = "database_cdc"
)

type ReviewPriority string

const (
	PriorityLow      ReviewPriority = "low"
	PriorityNormal   ReviewPriority = "normal"
	PriorityHigh     ReviewPriority = "high"
	PriorityCritical ReviewPriority = "critical"
)

type SuspensionReason string

const (
	ReasonPolicyViolation SuspensionReason = "policy_violation"
	ReasonPaymentFailure  SuspensionReason = "payment_failure"
	ReasonManual          SuspensionReason = "manual"
)

type HTTPMethod string

const (
	MethodGET  HTTPMethod = "GET"
	MethodPOST HTTPMethod = "POST"
)

type SettingsBlock struct {
	RetryMax        int     `json:"retry_max" validate:"min=0,max=10"`
	TimeoutSeconds  int     `json:"timeout_seconds" validate:"required,min=10,max=3600"`
	NotifyOnFailure bool    `json:"notify_on_failure"`
	WebhookURL      *string `json:"webhook_url" validate:"omitempty,url"`
}

type WorkspaceConfig struct {
	ID             string        `json:"id" validate:"required,uuid4"`
	Name           string        `json:"name" validate:"required,min=3,max=100"`
	Slug           string        `json:"slug" validate:"required,min=2,max=50,slug_format"`
	OwnerEmail     string        `json:"owner_email" validate:"required,email"`
	Plan           PlanType      `json:"plan" validate:"required,oneof=free pro enterprise"`
	MaxSyncRuns    int           `json:"max_sync_runs" validate:"required,min=1,max=1000"`
	Settings       SettingsBlock `json:"settings" validate:"required"`
	Tags           []string      `json:"tags" validate:"max=20,dive,min=1,max=50"`
	CreatedAt      time.Time     `json:"created_at"`
	SuspendedUntil *time.Time    `json:"suspended_until"`
}

type SyncRun struct {
	RunID           string      `json:"run_id" validate:"required,uuid4"`
	WorkspaceID     string      `json:"workspace_id" validate:"required,uuid4"`
	Status          SyncStatus  `json:"status" validate:"required,oneof=pending running succeeded failed cancelled"`
	Trigger         TriggerType `json:"trigger" validate:"required,oneof=manual scheduled webhook"`
	StartedAt       *time.Time  `json:"started_at"`
	FinishedAt      *time.Time  `json:"finished_at"`
	DurationMs      *int64      `json:"duration_ms" validate:"omitempty,min=0"`
	RecordsIngested *int64      `json:"records_ingested" validate:"omitempty,min=0,max=10000000"`
	ErrorCode       *string     `json:"error_code"`
	// Cross-field validation (finished_at >= started_at, duration_ms required
	// when finished_at is set) is implemented in validate/validate.go using
	// a manual post-validation check.
}

type SyncCompletedData struct {
	RunID           string `json:"run_id" validate:"required,uuid4"`
	WorkspaceID     string `json:"workspace_id" validate:"required,uuid4"`
	DurationMs      int64  `json:"duration_ms" validate:"min=0"`
	RecordsIngested int64  `json:"records_ingested" validate:"min=0,max=10000000"`
}

type SyncFailedData struct {
	RunID        string `json:"run_id" validate:"required,uuid4"`
	WorkspaceID  string `json:"workspace_id" validate:"required,uuid4"`
	ErrorCode    string `json:"error_code" validate:"required,min=1"`
	ErrorMessage string `json:"error_message" validate:"required,max=500"`
}

type WorkspaceSuspendedData struct {
	WorkspaceID    string           `json:"workspace_id" validate:"required,uuid4"`
	SuspendedUntil time.Time        `json:"suspended_until"`
	Reason         SuspensionReason `json:"reason" validate:"required,oneof=policy_violation payment_failure manual"`
}

type WebhookPayload struct {
	EventType      WebhookEventType `json:"event_type" validate:"required,oneof=sync.completed sync.failed workspace.suspended"`
	PayloadVersion string           `json:"payload_version" validate:"required,oneof=v1 v2 v3"`
	Timestamp      time.Time        `json:"timestamp"`
	Signature      string           `json:"signature" validate:"required,hex64"`
	// Go requires manual type dispatch for discriminated unions. The data field
	// is parsed after reading event_type.
	Data json.RawMessage `json:"data" validate:"required"`
}

type HttpPollConfig struct {
	URL     string            `json:"url" validate:"required,url"`
	Method  HTTPMethod        `json:"method" validate:"required,oneof=GET POST"`
	Headers map[string]string `json:"headers" validate:"required,max=20"`
}

type WebhookPushConfig struct {
	Path   string `json:"path" validate:"required,startswith=/"`
	Secret string `json:"secret" validate:"required,min=1"`
}

type FileWatchConfig struct {
	Path    string `json:"path" validate:"required,min=1"`
	Pattern string `json:"pattern" validate:"required,min=1"`
}

type DatabaseCDCConfig struct {
	DSN         string `json:"dsn" validate:"required,min=1"`
	Table       string `json:"table" validate:"required,min=1"`
	CursorField string `json:"cursor_field" validate:"required,min=1"`
}

type IngestionSource struct {
	SourceID            string          `json:"source_id" validate:"required,uuid4"`
	SourceType          SourceType      `json:"source_type" validate:"required,oneof=http_poll webhook_push file_watch database_cdc"`
	Config              json.RawMessage `json:"config" validate:"required"`
	Enabled             bool            `json:"enabled"`
	PollIntervalSeconds *int            `json:"poll_interval_seconds"`
	// Cross-field validation for source_type-specific config and
	// poll_interval_seconds lives in validate/validate.go.
}

type ReviewRequest struct {
	RequestID      string         `json:"request_id" validate:"required,uuid4"`
	WorkspaceID    string         `json:"workspace_id" validate:"required,uuid4"`
	ReviewerEmails []string       `json:"reviewer_emails" validate:"required,min=1,max=5,dive,email"`
	ContentIDs     []string       `json:"content_ids" validate:"required,min=1,max=50,dive,uuid4"`
	Priority       ReviewPriority `json:"priority" validate:"required,oneof=low normal high critical"`
	DueAt          *time.Time     `json:"due_at"`
	Notes          *string        `json:"notes" validate:"omitempty,max=2000"`
	// Cross-field validation (critical requires due_at, duplicate detection) is
	// implemented in validate/validate.go.
}
