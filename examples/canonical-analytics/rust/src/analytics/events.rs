use super::{match_date, match_multi, EventCountSeries};
use crate::data::models::Event;
use crate::filters::FilterState;
use std::collections::{BTreeMap, HashMap};

pub fn aggregate_events(data: &[Event], filters: &FilterState) -> EventCountSeries {
    if data.is_empty() {
        return EventCountSeries::default();
    }

    let mut env_dates: HashMap<String, BTreeMap<String, i64>> = HashMap::new();
    let mut all_dates: BTreeMap<String, i64> = BTreeMap::new();
    let mut environments_seen = Vec::new();

    for ev in data {
        if !match_date(&ev.timestamp, &filters.date_from, &filters.date_to) {
            continue;
        }
        if !match_multi(&ev.service, &filters.services) {
            continue;
        }
        if !match_multi(&ev.environment, &filters.environment) {
            continue;
        }

        let date = ev.timestamp.split('T').next().unwrap_or(&ev.timestamp).to_string();
        
        *all_dates.entry(date.clone()).or_insert(0) += ev.count;

        let env_map = env_dates.entry(ev.environment.clone()).or_default();
        *env_map.entry(date).or_insert(0) += ev.count;

        if !environments_seen.contains(&ev.environment) {
            environments_seen.push(ev.environment.clone());
        }
    }

    let dates: Vec<String> = all_dates.keys().cloned().collect();
    let counts: Vec<i64> = all_dates.values().cloned().collect();

    let mut by_environment = HashMap::new();
    for env in environments_seen {
        let env_map = env_dates.get(&env).unwrap();
        let env_counts: Vec<i64> = dates.iter().map(|d| *env_map.get(d).unwrap_or(&0)).collect();
        by_environment.insert(env, env_counts);
    }

    EventCountSeries {
        dates,
        counts,
        by_environment,
    }
}
