use crate::core::models::Job;

pub fn filter_jobs(jobs: &[Job], status: Option<&str>, tag: Option<&str>) -> Vec<Job> {
    jobs.iter()
        .filter(|job| {
            status
                .map(|value| job.status.as_str() == value)
                .unwrap_or(true)
        })
        .filter(|job| {
            tag.map(|value| job.tags.iter().any(|item| item == value))
                .unwrap_or(true)
        })
        .cloned()
        .collect()
}

pub fn sort_jobs(jobs: &[Job]) -> Vec<Job> {
    let mut items = jobs.to_vec();
    items.sort_by(|left, right| {
        right
            .started_at
            .cmp(&left.started_at)
            .then_with(|| left.name.cmp(&right.name))
    });
    items
}
