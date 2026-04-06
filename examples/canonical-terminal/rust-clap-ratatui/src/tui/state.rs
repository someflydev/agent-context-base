use crate::core::models::{Event, Job};

pub struct AppState {
    pub jobs: Vec<Job>,
    pub events: Vec<Event>,
    pub selected: usize,
    pub filter_failed_only: bool,
    pub scroll: u16,
}

impl AppState {
    pub fn new(jobs: Vec<Job>, events: Vec<Event>) -> Self {
        Self {
            jobs,
            events,
            selected: 0,
            filter_failed_only: false,
            scroll: 0,
        }
    }

    pub fn visible_jobs(&self) -> Vec<Job> {
        let mut jobs: Vec<Job> = self
            .jobs
            .iter()
            .filter(|job| !self.filter_failed_only || job.status.as_str() == "failed")
            .cloned()
            .collect();
        jobs.sort_by(|left, right| right.started_at.cmp(&left.started_at));
        jobs
    }

    pub fn selected_job(&self) -> Option<Job> {
        self.visible_jobs().get(self.selected).cloned()
    }

    pub fn next(&mut self) {
        let len = self.visible_jobs().len();
        if len > 0 {
            self.selected = (self.selected + 1).min(len.saturating_sub(1));
        }
    }

    pub fn previous(&mut self) {
        self.selected = self.selected.saturating_sub(1);
    }

    pub fn toggle_filter(&mut self) {
        self.filter_failed_only = !self.filter_failed_only;
        self.selected = 0;
    }
}
