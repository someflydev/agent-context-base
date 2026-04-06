use anyhow::Result;

use crate::core::models::{Job, Stats};

pub fn marker_block(begin: &str, content: &str, end: &str) {
    println!("{begin}");
    if !content.is_empty() {
        println!("{content}");
    }
    println!("{end}");
}

pub fn print_json<T: serde::Serialize>(value: &T) -> Result<()> {
    println!("{}", serde_json::to_string_pretty(value)?);
    Ok(())
}

pub fn jobs_table(jobs: &[Job]) -> String {
    let mut lines = vec![format!(
        "{:<8} {:<24} {:<8} {:<12} {}",
        "ID", "NAME", "STATUS", "DURATION", "TAGS"
    )];
    for job in jobs {
        lines.push(format!(
            "{:<8} {:<24} {:<8} {:<12} {}",
            job.id,
            job.name,
            job.status.as_str(),
            job.duration_s
                .map(|value| format!("{value:.1}s"))
                .unwrap_or_else(|| "-".to_string()),
            job.tags.join(",")
        ));
    }
    lines.join("\n")
}

pub fn job_plain(job: &Job) -> String {
    let mut lines = vec![
        format!("ID: {}", job.id),
        format!("Name: {}", job.name),
        format!("Status: {}", job.status.as_str()),
        format!(
            "Started: {}",
            job.started_at.clone().unwrap_or_else(|| "-".to_string())
        ),
        format!(
            "Duration (s): {}",
            job.duration_s
                .map(|value| format!("{value:.1}"))
                .unwrap_or_else(|| "-".to_string())
        ),
        format!("Tags: {}", job.tags.join(", ")),
        "Output:".to_string(),
    ];
    for line in &job.output_lines {
        lines.push(format!("  - {line}"));
    }
    lines.join("\n")
}

pub fn stats_plain(stats: &Stats) -> String {
    vec![
        format!("Total jobs: {}", stats.total),
        format!(
            "Done: {}",
            stats.by_status.get("done").copied().unwrap_or(0)
        ),
        format!(
            "Failed: {}",
            stats.by_status.get("failed").copied().unwrap_or(0)
        ),
        format!(
            "Running: {}",
            stats.by_status.get("running").copied().unwrap_or(0)
        ),
        format!(
            "Pending: {}",
            stats.by_status.get("pending").copied().unwrap_or(0)
        ),
        format!("Average duration (s): {:.2}", stats.avg_duration_s),
        format!("Failure rate: {:.2}", stats.failure_rate),
    ]
    .join("\n")
}
