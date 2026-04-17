use super::{match_date, match_multi, IncidentSeverity};
use crate::data::models::{Incident, Service};
use crate::filters::FilterState;
use std::collections::{HashMap, HashSet};

pub fn aggregate_incident_severity(
    incidents: &[Incident],
    services: &[Service],
    filters: &FilterState,
) -> IncidentSeverity {
    let valid_services: HashSet<String> = services.iter().map(|s| s.name.clone()).collect();

    let mut counts_map: HashMap<String, i64> = HashMap::new();
    let mut mttr_sum: HashMap<String, f64> = HashMap::new();

    for i in incidents {
        if !match_date(&i.timestamp, &filters.date_from, &filters.date_to) {
            continue;
        }
        if !match_multi(&i.environment, &filters.environment) {
            continue;
        }
        if !match_multi(&i.severity, &filters.severity) {
            continue;
        }
        if !valid_services.contains(&i.service) {
            continue;
        }
        if !match_multi(&i.service, &filters.services) {
            continue;
        }

        *counts_map.entry(i.severity.clone()).or_insert(0) += 1;
        *mttr_sum.entry(i.severity.clone()).or_insert(0.0) += i.mttr_mins;
    }

    if counts_map.is_empty() {
        return IncidentSeverity {
            severities: Vec::new(),
            counts: Vec::new(),
            mttr_by_severity: HashMap::new(),
        };
    }

    let order = vec!["critical", "high", "medium", "low", "sev1", "sev2", "sev3", "sev4"];
    let mut severities = Vec::new();
    let mut counts = Vec::new();
    let mut mttr_by_severity = HashMap::new();

    for sev in order {
        if let Some(&count) = counts_map.get(sev) {
            let sum = *mttr_sum.get(sev).unwrap();
            severities.push(sev.to_string());
            counts.push(count);
            mttr_by_severity.insert(sev.to_string(), sum / count as f64);
        }
    }

    IncidentSeverity {
        severities,
        counts,
        mttr_by_severity,
    }
}
