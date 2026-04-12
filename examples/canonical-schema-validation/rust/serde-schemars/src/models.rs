use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum PlanType {
    Free,
    Pro,
    Enterprise,
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub struct SettingsBlock {
    #[schemars(description = "Maximum retry count from 0 to 10.")]
    pub retry_max: u8,
    #[schemars(description = "Timeout in seconds from 10 to 3600.")]
    pub timeout_seconds: u16,
    #[schemars(description = "Whether failures trigger notifications.")]
    pub notify_on_failure: bool,
    #[schemars(description = "Optional webhook endpoint when notifications are mirrored.")]
    pub webhook_url: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub struct WorkspaceConfig {
    #[schemars(description = "Workspace UUID as serialized on the wire.")]
    pub id: String,
    #[schemars(description = "Human-friendly workspace name.")]
    pub name: String,
    #[schemars(description = "Slug used in URLs and CLI references.")]
    pub slug: String,
    #[schemars(description = "Primary owner email address.")]
    pub owner_email: String,
    #[schemars(description = "Plan tier selector.")]
    pub plan: PlanType,
    #[schemars(description = "Maximum allowed sync runs for the workspace.")]
    pub max_sync_runs: u32,
    #[schemars(description = "Nested runtime settings block.")]
    pub settings: SettingsBlock,
    #[schemars(description = "Operator-defined workspace tags.")]
    pub tags: Vec<String>,
    #[schemars(description = "Workspace creation timestamp in RFC 3339 format.")]
    pub created_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[schemars(description = "Optional suspension end timestamp. Omitted when absent.")]
    pub suspended_until: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum SyncStatus {
    Pending,
    Running,
    Succeeded,
    Failed,
    Cancelled,
}

#[derive(Debug, Deserialize, Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub struct SyncRun {
    #[schemars(description = "Sync run UUID.")]
    pub run_id: String,
    #[schemars(description = "Workspace UUID owning the run.")]
    pub workspace_id: String,
    #[schemars(description = "Status emitted on the wire.")]
    pub status: SyncStatus,
    #[schemars(description = "Optional start timestamp.")]
    pub started_at: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[schemars(description = "Optional finish timestamp. Omitted while unfinished.")]
    pub finished_at: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[schemars(description = "Optional duration in milliseconds.")]
    pub duration_ms: Option<u64>,
}

// No runtime-validator attributes live in this file.
// This is the contract lane: schemars generates JSON Schema.
// Use rust/validator/ or rust/garde/ for runtime validation.
