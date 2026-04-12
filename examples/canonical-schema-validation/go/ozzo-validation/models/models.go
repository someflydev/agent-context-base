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
type TriggerType string
type ReviewPriority string
type WebhookEventType string
type SourceType string
type SuspensionReason string
type HTTPMethod string

const (
	SyncPending   SyncStatus = "pending"
	SyncRunning   SyncStatus = "running"
	SyncSucceeded SyncStatus = "succeeded"
	SyncFailed    SyncStatus = "failed"
	SyncCancelled SyncStatus = "cancelled"

	TriggerManual    TriggerType = "manual"
	TriggerScheduled TriggerType = "scheduled"
	TriggerWebhook   TriggerType = "webhook"

	PriorityLow      ReviewPriority = "low"
	PriorityNormal   ReviewPriority = "normal"
	PriorityHigh     ReviewPriority = "high"
	PriorityCritical ReviewPriority = "critical"

	WebhookSyncCompleted WebhookEventType = "sync.completed"
	WebhookSyncFailed    WebhookEventType = "sync.failed"
	WebhookSuspended     WebhookEventType = "workspace.suspended"

	SourceHTTPPoll   SourceType = "http_poll"
	SourceWebhook    SourceType = "webhook_push"
	SourceFileWatch  SourceType = "file_watch"
	SourceDatabaseCD SourceType = "database_cdc"

	ReasonPolicyViolation SuspensionReason = "policy_violation"
	ReasonPaymentFailure  SuspensionReason = "payment_failure"
	ReasonManual          SuspensionReason = "manual"

	MethodGET  HTTPMethod = "GET"
	MethodPOST HTTPMethod = "POST"
)

type SettingsBlock struct {
	RetryMax        int     `json:"retry_max"`
	TimeoutSeconds  int     `json:"timeout_seconds"`
	NotifyOnFailure bool    `json:"notify_on_failure"`
	WebhookURL      *string `json:"webhook_url"`
}

type WorkspaceConfig struct {
	ID             string        `json:"id"`
	Name           string        `json:"name"`
	Slug           string        `json:"slug"`
	OwnerEmail     string        `json:"owner_email"`
	Plan           PlanType      `json:"plan"`
	MaxSyncRuns    int           `json:"max_sync_runs"`
	Settings       SettingsBlock `json:"settings"`
	Tags           []string      `json:"tags"`
	CreatedAt      time.Time     `json:"created_at"`
	SuspendedUntil *time.Time    `json:"suspended_until"`
}

type SyncRun struct {
	RunID           string      `json:"run_id"`
	WorkspaceID     string      `json:"workspace_id"`
	Status          SyncStatus  `json:"status"`
	Trigger         TriggerType `json:"trigger"`
	StartedAt       *time.Time  `json:"started_at"`
	FinishedAt      *time.Time  `json:"finished_at"`
	DurationMs      *int64      `json:"duration_ms"`
	RecordsIngested *int64      `json:"records_ingested"`
	ErrorCode       *string     `json:"error_code"`
}

type SyncCompletedData struct {
	RunID           string `json:"run_id"`
	WorkspaceID     string `json:"workspace_id"`
	DurationMs      int64  `json:"duration_ms"`
	RecordsIngested int64  `json:"records_ingested"`
}

type SyncFailedData struct {
	RunID        string `json:"run_id"`
	WorkspaceID  string `json:"workspace_id"`
	ErrorCode    string `json:"error_code"`
	ErrorMessage string `json:"error_message"`
}

type WorkspaceSuspendedData struct {
	WorkspaceID    string           `json:"workspace_id"`
	SuspendedUntil time.Time        `json:"suspended_until"`
	Reason         SuspensionReason `json:"reason"`
}

type WebhookPayload struct {
	EventType      WebhookEventType `json:"event_type"`
	PayloadVersion string           `json:"payload_version"`
	Timestamp      time.Time        `json:"timestamp"`
	Signature      string           `json:"signature"`
	Data           json.RawMessage  `json:"data"`
}

type HttpPollConfig struct {
	URL     string            `json:"url"`
	Method  HTTPMethod        `json:"method"`
	Headers map[string]string `json:"headers"`
}

type WebhookPushConfig struct {
	Path   string `json:"path"`
	Secret string `json:"secret"`
}

type FileWatchConfig struct {
	Path    string `json:"path"`
	Pattern string `json:"pattern"`
}

type DatabaseCDCConfig struct {
	DSN         string `json:"dsn"`
	Table       string `json:"table"`
	CursorField string `json:"cursor_field"`
}

type IngestionSource struct {
	SourceID            string          `json:"source_id"`
	SourceType          SourceType      `json:"source_type"`
	Config              json.RawMessage `json:"config"`
	Enabled             bool            `json:"enabled"`
	PollIntervalSeconds *int            `json:"poll_interval_seconds"`
}

type ReviewRequest struct {
	RequestID      string         `json:"request_id"`
	WorkspaceID    string         `json:"workspace_id"`
	ReviewerEmails []string       `json:"reviewer_emails"`
	ContentIDs     []string       `json:"content_ids"`
	Priority       ReviewPriority `json:"priority"`
	DueAt          *time.Time     `json:"due_at"`
	Notes          *string        `json:"notes"`
}
