use std::collections::HashMap;

use crate::core::models::{Job, JobStatus, Stats};

pub fn compute_stats(jobs: &[Job]) -> Stats {
    let mut by_status: HashMap<String, usize> = HashMap::from([
        (JobStatus::Pending.as_str().to_string(), 0),
        (JobStatus::Running.as_str().to_string(), 0),
        (JobStatus::Done.as_str().to_string(), 0),
        (JobStatus::Failed.as_str().to_string(), 0),
    ]);
    let mut durations = Vec::new();
    for job in jobs {
        *by_status
            .entry(job.status.as_str().to_string())
            .or_default() += 1;
        if let Some(duration) = job.duration_s {
            durations.push(duration);
        }
    }
    let total = jobs.len();
    let avg_duration_s = if durations.is_empty() {
        0.0
    } else {
        let sum: f64 = durations.iter().sum();
        (sum / durations.len() as f64 * 100.0).round() / 100.0
    };
    let failed = *by_status.get("failed").unwrap_or(&0);
    let failure_rate = if total == 0 {
        0.0
    } else {
        ((failed as f64 / total as f64) * 100.0).round() / 100.0
    };
    Stats {
        total,
        by_status,
        avg_duration_s,
        failure_rate,
    }
}
