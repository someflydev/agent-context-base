//! Lane A example using the `garde` crate.
//! garde provides a richer attribute DSL than `validator`:
//! - inner() for per-element validation in collections
//! - pattern() for inline regex (no Lazy<Regex> needed)
//! - context-based validation for cross-field rules
//! Like validator, garde handles constraint checking only.
//! serde handles deserialization; schemars handles schema export.

use garde::Validate;
use serde::{Deserialize, Serialize};

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

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct WorkspaceConfig {
    #[garde(length(min = 3, max = 100))]
    pub name: String,
    #[garde(pattern(r"^[a-z][a-z0-9-]{1,48}[a-z0-9]$"))]
    pub slug: String,
    #[garde(email)]
    pub owner_email: String,
    #[garde(skip)]
    pub plan: PlanType,
    #[garde(range(min = 1, max = 1000))]
    pub max_sync_runs: u32,
    #[garde(length(max = 20), inner(length(min = 1, max = 50)))]
    pub tags: Vec<String>,
}

#[derive(Debug, Deserialize, Serialize, Validate)]
pub struct SyncRun {
    #[garde(skip)]
    pub status: SyncStatus,
    #[garde(skip)]
    pub started_at: Option<String>,
    #[garde(skip)]
    pub finished_at: Option<String>,
    #[garde(range(min = 0))]
    pub duration_ms: Option<u64>,
}

pub fn validate_workspace_cross_fields(cfg: &WorkspaceConfig) -> garde::Result {
    match cfg.plan {
        PlanType::Free if cfg.max_sync_runs > 10 => {
            Err(garde::Error::new("free plan supports at most 10 sync runs"))
        }
        PlanType::Pro if cfg.max_sync_runs > 100 => {
            Err(garde::Error::new("pro plan supports at most 100 sync runs"))
        }
        _ => Ok(()),
    }
}

pub fn validate_sync_cross_fields(run: &SyncRun) -> garde::Result {
    if run.finished_at.is_some() && run.started_at.is_none() {
        return Err(garde::Error::new(
            "started_at is required when finished_at is set",
        ));
    }
    if let (Some(started_at), Some(finished_at)) = (&run.started_at, &run.finished_at) {
        if finished_at < started_at {
            return Err(garde::Error::new("finished_at must be >= started_at"));
        }
    }
    if run.finished_at.is_some() && run.duration_ms.is_none() {
        return Err(garde::Error::new(
            "duration_ms is required when finished_at is set",
        ));
    }
    Ok(())
}
