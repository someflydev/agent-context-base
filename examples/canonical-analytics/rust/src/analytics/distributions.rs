use super::{match_date, match_multi, LatencyByService, LatencyHistogram};
use crate::data::models::LatencySample;
use crate::filters::FilterState;
use std::collections::HashMap;

pub fn percentile(values: &mut [f64], p: f64) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    values.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let idx = ((values.len() as f64 * p / 100.0) as usize).min(values.len() - 1);
    values[idx]
}

pub fn aggregate_latency_histogram(
    data: &[LatencySample],
    filters: &FilterState,
) -> LatencyHistogram {
    if data.is_empty() {
        return LatencyHistogram::default();
    }

    let mut values = Vec::new();
    for sample in data {
        if !match_date(&sample.timestamp, &filters.date_from, &filters.date_to) {
            continue;
        }
        if !match_multi(&sample.service, &filters.services) {
            continue;
        }
        if !match_multi(&sample.environment, &filters.environment) {
            continue;
        }
        values.push(sample.latency_ms);
    }

    if values.is_empty() {
        return LatencyHistogram::default();
    }

    let mut sorted_vals = values.clone();
    let p50 = percentile(&mut sorted_vals, 50.0);
    let p95 = percentile(&mut sorted_vals, 95.0);
    let p99 = percentile(&mut sorted_vals, 99.0);

    LatencyHistogram {
        values,
        p50,
        p95,
        p99,
    }
}

pub fn aggregate_latency_by_service(
    data: &[LatencySample],
    filters: &FilterState,
) -> LatencyByService {
    if data.is_empty() {
        return LatencyByService::default();
    }

    let mut by_srv: HashMap<String, Vec<f64>> = HashMap::new();
    for sample in data {
        if !match_date(&sample.timestamp, &filters.date_from, &filters.date_to) {
            continue;
        }
        if !match_multi(&sample.service, &filters.services) {
            continue;
        }
        if !match_multi(&sample.environment, &filters.environment) {
            continue;
        }
        by_srv
            .entry(sample.service.clone())
            .or_default()
            .push(sample.latency_ms);
    }

    let mut services = Vec::new();
    let mut p50s = Vec::new();
    let mut p95s = Vec::new();
    let mut p99s = Vec::new();

    let mut keys: Vec<String> = by_srv.keys().cloned().collect();
    keys.sort();

    for k in keys {
        let mut vals = by_srv.get(&k).unwrap().clone();
        services.push(k);
        p50s.push(percentile(&mut vals, 50.0));
        p95s.push(percentile(&mut vals, 95.0));
        p99s.push(percentile(&mut vals, 99.0));
    }

    LatencyByService {
        services,
        p50s,
        p95s,
        p99s,
    }
}
