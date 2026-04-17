pub mod distributions;
pub mod events;
pub mod funnel;
pub mod heatmap;
pub mod incidents;
pub mod services;

use std::collections::HashMap;

#[derive(Debug, Default)]
pub struct EventCountSeries {
    pub dates: Vec<String>,
    pub counts: Vec<i64>,
    pub by_environment: HashMap<String, Vec<i64>>,
}

#[derive(Debug, Default)]
pub struct ServiceErrorRates {
    pub services: Vec<String>,
    pub error_rates: Vec<f64>,
    pub total_events: Vec<i64>,
}

#[derive(Debug, Default)]
pub struct LatencyHistogram {
    pub values: Vec<f64>,
    pub p50: f64,
    pub p95: f64,
    pub p99: f64,
}

#[derive(Debug, Default)]
pub struct LatencyByService {
    pub services: Vec<String>,
    pub p50s: Vec<f64>,
    pub p95s: Vec<f64>,
    pub p99s: Vec<f64>,
}

#[derive(Debug, Default)]
pub struct EventHeatmap {
    pub hours: Vec<i32>,
    pub days: Vec<String>,
    pub counts: Vec<Vec<i64>>,
}

#[derive(Debug, Default)]
pub struct FunnelStages {
    pub stages: Vec<String>,
    pub counts: Vec<i64>,
    pub drop_off_rates: Vec<f64>,
}

#[derive(Debug, Default)]
pub struct IncidentSeverity {
    pub severities: Vec<String>,
    pub counts: Vec<i64>,
    pub mttr_by_severity: HashMap<String, f64>,
}

// Helpers for filter matching
pub fn match_date(ts: &str, from: &Option<String>, to: &Option<String>) -> bool {
    let date = ts.split('T').next().unwrap_or(ts);
    if let Some(f) = from {
        if date < f.as_str() {
            return false;
        }
    }
    if let Some(t) = to {
        if date > t.as_str() {
            return false;
        }
    }
    true
}

pub fn match_multi(val: &str, valid: &[String]) -> bool {
    valid.is_empty() || valid.iter().any(|v| v == val)
}
