use analytics_workbench_rust::analytics::distributions::{
    aggregate_latency_histogram, percentile,
};
use analytics_workbench_rust::analytics::events::aggregate_events;
use analytics_workbench_rust::analytics::funnel::aggregate_funnel_stages;
use analytics_workbench_rust::analytics::heatmap::aggregate_event_heatmap;
use analytics_workbench_rust::analytics::incidents::aggregate_incident_severity;
use analytics_workbench_rust::analytics::services::aggregate_services;
use analytics_workbench_rust::data::loader::{get_fixture_path, load_fixtures};
use analytics_workbench_rust::filters::FilterState;

#[test]
fn test_aggregate_events_with_smoke_fixture() {
    let store = load_fixtures(&get_fixture_path()).unwrap();
    let filters = FilterState::default();
    let result = aggregate_events(&store.events, &filters);
    assert!(!result.dates.is_empty());
    assert!(!result.counts.is_empty());
    assert_eq!(result.dates.len(), result.counts.len());
}

#[test]
fn test_aggregate_events_with_empty_input() {
    let filters = FilterState::default();
    let result = aggregate_events(&[], &filters);
    assert!(result.dates.is_empty());
    assert!(result.counts.is_empty());
    assert!(result.by_environment.is_empty());
}

#[test]
fn test_aggregate_events_filter_by_environment() {
    let store = load_fixtures(&get_fixture_path()).unwrap();
    let mut filters = FilterState::default();
    filters.environment = vec!["production".to_string()];
    let result = aggregate_events(&store.events, &filters);
    
    // Test that our aggregated by_environment counts reflect production
    // This assumes the fixture has a production environment.
    assert!(result.by_environment.contains_key("production"));
    // Other environments might exist but either shouldn't or should have 0/filtered out
}

#[test]
fn test_aggregate_services_with_smoke_fixture() {
    let store = load_fixtures(&get_fixture_path()).unwrap();
    let filters = FilterState::default();
    let result = aggregate_services(&store.services, &store.events, &filters);
    assert!(!result.services.is_empty());
    assert!(!result.error_rates.is_empty());
    assert!(!result.total_events.is_empty());
}

#[test]
fn test_aggregate_services_with_empty_input() {
    let filters = FilterState::default();
    let result = aggregate_services(&[], &[], &filters);
    assert!(result.services.is_empty());
    assert!(result.error_rates.is_empty());
    assert!(result.total_events.is_empty());
}

#[test]
fn test_aggregate_latency_histogram_with_smoke_fixture() {
    let store = load_fixtures(&get_fixture_path()).unwrap();
    let filters = FilterState::default();
    let result = aggregate_latency_histogram(&store.latency_samples, &filters);
    assert!(!result.values.is_empty());
    assert!(result.p50 > 0.0);
    assert!(result.p95 >= result.p50);
    assert!(result.p99 >= result.p95);
}

#[test]
fn test_aggregate_latency_histogram_empty_input() {
    let filters = FilterState::default();
    let result = aggregate_latency_histogram(&[], &filters);
    assert!(result.values.is_empty());
    assert_eq!(result.p50, 0.0);
}

#[test]
fn test_percentile_helper() {
    let mut values = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0];
    let p50 = percentile(&mut values, 50.0);
    assert_eq!(p50, 6.0); // 10 * 0.5 = 5th index -> 6.0
}

#[test]
fn test_aggregate_heatmap_with_smoke_fixture() {
    let store = load_fixtures(&get_fixture_path()).unwrap();
    let filters = FilterState::default();
    let result = aggregate_event_heatmap(&store.events, &filters);
    assert!(!result.hours.is_empty());
    assert!(!result.days.is_empty());
    assert!(!result.counts.is_empty());
}

#[test]
fn test_aggregate_funnel_with_smoke_fixture() {
    let store = load_fixtures(&get_fixture_path()).unwrap();
    let filters = FilterState::default();
    let result = aggregate_funnel_stages(&store.sessions, &store.funnel_stages, &filters);
    assert!(!result.stages.is_empty());
    assert!(!result.counts.is_empty());
    assert!(!result.drop_off_rates.is_empty());
}

#[test]
fn test_aggregate_incidents_with_smoke_fixture() {
    let store = load_fixtures(&get_fixture_path()).unwrap();
    let filters = FilterState::default();
    let result = aggregate_incident_severity(&store.incidents, &store.services, &filters);
    assert!(!result.severities.is_empty());
    assert!(!result.counts.is_empty());
}
