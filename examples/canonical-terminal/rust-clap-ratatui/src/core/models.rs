use std::collections::HashMap;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum JobStatus {
    Pending,
    Running,
    Done,
    Failed,
}

impl JobStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Pending => "pending",
            Self::Running => "running",
            Self::Done => "done",
            Self::Failed => "failed",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Job {
    pub id: String,
    pub name: String,
    pub status: JobStatus,
    pub started_at: Option<String>,
    pub duration_s: Option<f64>,
    pub tags: Vec<String>,
    pub output_lines: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub event_id: String,
    pub job_id: String,
    pub event_type: String,
    pub timestamp: String,
    pub message: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct Stats {
    pub total: usize,
    pub by_status: HashMap<String, usize>,
    pub avg_duration_s: f64,
    pub failure_rate: f64,
}
