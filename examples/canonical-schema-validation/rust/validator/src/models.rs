//! Lane A example using the `validator` crate.
//! serde handles deserialization (shape/wire format).
//! validator handles constraint checking (field-level rules).
//! schemars (in ../serde-schemars/) handles JSON Schema export (contract).
//! These are three distinct operations with three distinct libraries.

use once_cell::sync::Lazy;
use regex::Regex;
use serde::{Deserialize, Serialize};
use validator::{Validate, ValidationError, ValidationErrors};

static SLUG_REGEX: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^[a-z][a-z0-9-]{1,48}[a-z0-9]$").expect("valid slug regex"));
static RFC3339_REGEX: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$").expect("valid timestamp regex")
});
static SIGNATURE_REGEX: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"^[a-f0-9]{64}$").expect("valid signature regex"));

fn validate_url(value: &str) -> Result<(), ValidationError> {
    if value.starts_with("http://") || value.starts_with("https://") {
        Ok(())
    } else {
        Err(ValidationError::new("url"))
    }
}

fn validate_timestamp(value: &str) -> Result<(), ValidationError> {
    if RFC3339_REGEX.is_match(value) {
        Ok(())
    } else {
        Err(ValidationError::new("timestamp"))
    }
}

fn validate_signature(value: &str) -> Result<(), ValidationError> {
    if SIGNATURE_REGEX.is_match(value) {
        Ok(())
    } else {
        Err(ValidationError::new("signature"))
    }
}

fn validate_tag_items(value: &[String]) -> Result<(), ValidationError> {
    if value.iter().all(|item| (1..=50).contains(&item.len())) {
        Ok(())
    } else {
        Err(ValidationError::new("tag_item_length"))
    }
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct SettingsBlock {
    #[validate(range(min = 0, max = 10))]
    pub retry_max: u8,
    #[validate(range(min = 10, max = 3600))]
    pub timeout_seconds: u16,
    pub notify_on_failure: bool,
    #[validate(custom(function = "validate_url"))]
    pub webhook_url: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum PlanType {
    Free,
    Pro,
    Enterprise,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum SyncStatus {
    Pending,
    Running,
    Succeeded,
    Failed,
    Cancelled,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum TriggerType {
    Manual,
    Scheduled,
    Webhook,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SourceType {
    HttpPoll,
    WebhookPush,
    FileWatch,
    DatabaseCdc,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum ReviewPriority {
    Low,
    Normal,
    High,
    Critical,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum HttpMethod {
    GET,
    POST,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct WorkspaceConfig {
    pub id: String,
    #[validate(length(min = 3, max = 100))]
    pub name: String,
    #[validate(regex(path = *SLUG_REGEX))]
    pub slug: String,
    #[validate(email)]
    pub owner_email: String,
    pub plan: PlanType,
    #[validate(range(min = 1, max = 1000))]
    pub max_sync_runs: u32,
    #[validate(nested)]
    pub settings: SettingsBlock,
    #[validate(length(max = 20), custom(function = "validate_tag_items"))]
    pub tags: Vec<String>,
    #[validate(custom(function = "validate_timestamp"))]
    pub created_at: String,
    #[validate(custom(function = "validate_timestamp"))]
    pub suspended_until: Option<String>,
}

fn validate_optional_timestamp(value: &str) -> Result<(), ValidationError> {
    validate_timestamp(value)
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct SyncRun {
    pub run_id: String,
    pub workspace_id: String,
    pub status: SyncStatus,
    pub trigger: TriggerType,
    #[validate(custom(function = "validate_optional_timestamp"))]
    pub started_at: Option<String>,
    #[validate(custom(function = "validate_optional_timestamp"))]
    pub finished_at: Option<String>,
    #[validate(range(min = 0))]
    pub duration_ms: Option<u64>,
    #[validate(range(min = 0, max = 10000000))]
    pub records_ingested: Option<u64>,
    pub error_code: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct SyncCompletedData {
    pub run_id: String,
    pub workspace_id: String,
    #[validate(range(min = 0))]
    pub duration_ms: u64,
    #[validate(range(min = 0, max = 10000000))]
    pub records_ingested: u64,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct SyncFailedData {
    pub run_id: String,
    pub workspace_id: String,
    #[validate(length(min = 1))]
    pub error_code: String,
    #[validate(length(min = 1, max = 500))]
    pub error_message: String,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct WorkspaceSuspendedData {
    pub workspace_id: String,
    #[validate(custom(function = "validate_timestamp"))]
    pub suspended_until: String,
    pub reason: SuspensionReason,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SuspensionReason {
    PolicyViolation,
    PaymentFailure,
    Manual,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct WebhookPayload {
    pub payload_version: String,
    pub timestamp: String,
    pub signature: String,
    #[serde(flatten)]
    pub data: WebhookData,
}

/// Rust's serde provides native discriminated union support via
/// #[serde(tag = ..., content = ...)] or #[serde(tag = ...)]. This is more
/// ergonomic than Go's manual dispatch.
#[derive(Debug, Deserialize, Serialize)]
#[serde(tag = "event_type", content = "data")]
pub enum WebhookData {
    #[serde(rename = "sync.completed")]
    SyncCompleted(SyncCompletedData),
    #[serde(rename = "sync.failed")]
    SyncFailed(SyncFailedData),
    #[serde(rename = "workspace.suspended")]
    WorkspaceSuspended(WorkspaceSuspendedData),
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct HttpPollConfig {
    pub url: String,
    pub method: HttpMethod,
    pub headers: std::collections::BTreeMap<String, String>,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct WebhookPushConfig {
    #[validate(length(min = 1))]
    pub path: String,
    #[validate(length(min = 1))]
    pub secret: String,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct FileWatchConfig {
    #[validate(length(min = 1))]
    pub path: String,
    #[validate(length(min = 1))]
    pub pattern: String,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct DatabaseCdcConfig {
    #[validate(length(min = 1))]
    pub dsn: String,
    #[validate(length(min = 1))]
    pub table: String,
    #[validate(length(min = 1))]
    pub cursor_field: String,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(tag = "source_type", content = "config")]
pub enum SourceConfig {
    #[serde(rename = "http_poll")]
    HttpPoll(HttpPollConfig),
    #[serde(rename = "webhook_push")]
    WebhookPush(WebhookPushConfig),
    #[serde(rename = "file_watch")]
    FileWatch(FileWatchConfig),
    #[serde(rename = "database_cdc")]
    DatabaseCdc(DatabaseCdcConfig),
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct IngestionSource {
    pub source_id: String,
    pub enabled: bool,
    pub poll_interval_seconds: Option<u32>,
    #[serde(flatten)]
    pub config: SourceConfig,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct ReviewRequest {
    pub request_id: String,
    pub workspace_id: String,
    #[validate(length(min = 1, max = 5))]
    pub reviewer_emails: Vec<String>,
    #[validate(length(min = 1, max = 50))]
    pub content_ids: Vec<String>,
    pub priority: ReviewPriority,
    #[validate(custom(function = "validate_optional_timestamp"))]
    pub due_at: Option<String>,
    #[validate(length(max = 2000))]
    pub notes: Option<String>,
}

/// validator's derive macro handles field-level rules. Cross-field rules
/// require a separate function. The Validate trait's validate() method only
/// runs what is specified in #[validate(...)] attributes.
pub fn validate_cross_fields_sync_run(run: &SyncRun) -> Result<(), ValidationErrors> {
    let mut errors = ValidationErrors::new();
    if run.finished_at.is_some() && run.started_at.is_none() {
        errors.add("started_at", ValidationError::new("required_when_finished"));
    }
    if let (Some(started_at), Some(finished_at)) = (&run.started_at, &run.finished_at) {
        if finished_at < started_at {
            errors.add(
                "finished_at",
                ValidationError::new("must_be_after_started_at"),
            );
        }
    }
    if run.finished_at.is_some() && run.duration_ms.is_none() {
        errors.add(
            "duration_ms",
            ValidationError::new("required_when_finished"),
        );
    }
    if matches!(run.status, SyncStatus::Failed) && run.error_code.is_none() {
        errors.add(
            "error_code",
            ValidationError::new("required_for_failed_status"),
        );
    }
    if !matches!(run.status, SyncStatus::Failed) && run.error_code.is_some() {
        errors.add(
            "error_code",
            ValidationError::new("unexpected_for_non_failed_status"),
        );
    }
    if errors.is_empty() {
        Ok(())
    } else {
        Err(errors)
    }
}

pub fn validate_workspace_plan(cfg: &WorkspaceConfig) -> Result<(), ValidationErrors> {
    let mut errors = ValidationErrors::new();
    match cfg.plan {
        PlanType::Free if cfg.max_sync_runs > 10 => {
            errors.add("max_sync_runs", ValidationError::new("free_plan_limit"));
        }
        PlanType::Pro if cfg.max_sync_runs > 100 => {
            errors.add("max_sync_runs", ValidationError::new("pro_plan_limit"));
        }
        _ => {}
    }
    if errors.is_empty() {
        Ok(())
    } else {
        Err(errors)
    }
}

pub fn validate_webhook_payload(payload: &WebhookPayload) -> Result<(), ValidationErrors> {
    let mut errors = ValidationErrors::new();
    if !matches!(payload.payload_version.as_str(), "v1" | "v2" | "v3") {
        errors.add(
            "payload_version",
            ValidationError::new("invalid_payload_version"),
        );
    }
    if let Err(err) = validate_timestamp(&payload.timestamp) {
        errors.add("timestamp", err);
    }
    if let Err(err) = validate_signature(&payload.signature) {
        errors.add("signature", err);
    }
    let nested = match &payload.data {
        WebhookData::SyncCompleted(data) => data.validate(),
        WebhookData::SyncFailed(data) => data.validate(),
        WebhookData::WorkspaceSuspended(data) => data.validate(),
    };
    if nested.is_err() {
        errors.add("data", ValidationError::new("invalid_nested_payload"));
    }
    if errors.is_empty() {
        Ok(())
    } else {
        Err(errors)
    }
}
