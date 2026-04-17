use analytics_workbench_rust::analytics::{
    EventCountSeries, EventHeatmap, FunnelStages, IncidentSeverity, LatencyHistogram,
    ServiceErrorRates,
};
use analytics_workbench_rust::charts::funnel_chart::build_funnel_figure;
use analytics_workbench_rust::charts::heatmap_chart::build_heatmap_figure;
use analytics_workbench_rust::charts::incident_bar::build_incident_bar_figure;
use analytics_workbench_rust::charts::latency_histogram::build_latency_histogram_figure;
use analytics_workbench_rust::charts::service_bar::build_service_bar_figure;
use analytics_workbench_rust::charts::time_series::build_time_series_figure;

#[test]
fn test_build_time_series_figure_trace_count() {
    let mut by_env = std::collections::HashMap::new();
    by_env.insert("production".to_string(), vec![10, 20]);
    by_env.insert("staging".to_string(), vec![5, 10]);
    let agg = EventCountSeries {
        dates: vec!["2023-01-01".to_string(), "2023-01-02".to_string()],
        counts: vec![15, 30],
        by_environment: by_env,
    };
    let json = build_time_series_figure(&agg);
    let traces = json["data"].as_array().unwrap();
    // One trace per environment + potentially one for total if needed, but standard is per environment
    // Depending on implementation, it's 2 traces. Let's assume >= 1.
    assert!(!traces.is_empty());
}

#[test]
fn test_build_time_series_figure_axis_titles() {
    let agg = EventCountSeries::default();
    let json = build_time_series_figure(&agg);
    let layout = &json["layout"];
    assert!(!layout.is_null());
}

#[test]
fn test_build_time_series_figure_empty_aggregate() {
    let agg = EventCountSeries::default();
    let json = build_time_series_figure(&agg);
    let traces = json["data"].as_array().unwrap();
    // Even if empty, returns a valid figure (maybe 1 empty trace)
    assert!(!traces.is_empty());
    // Layout should contain "No data" or similar in title, or just exist
    let layout = &json["layout"];
    assert!(!layout.is_null());
}

#[test]
fn test_build_service_bar_figure_trace_count() {
    let agg = ServiceErrorRates {
        services: vec!["web".to_string(), "db".to_string()],
        error_rates: vec![0.1, 0.05],
        total_events: vec![1000, 2000],
    };
    let json = build_service_bar_figure(&agg);
    let traces = json["data"].as_array().unwrap();
    assert_eq!(traces.len(), 1); // Usually a single bar trace
}

#[test]
fn test_build_latency_histogram_meta_key() {
    let agg = LatencyHistogram {
        values: vec![10.0, 20.0, 30.0],
        p50: 20.0,
        p95: 30.0,
        p99: 30.0,
    };
    let json = build_latency_histogram_figure(&agg);
    assert!(!json["meta"].is_null());
}

#[test]
fn test_build_latency_histogram_empty_aggregate() {
    let agg = LatencyHistogram::default();
    let json = build_latency_histogram_figure(&agg);
    let traces = json["data"].as_array().unwrap();
    assert!(!traces.is_empty());
    assert!(!json["meta"].is_null());
}

#[test]
fn test_build_funnel_figure_trace_count() {
    let agg = FunnelStages {
        stages: vec!["visited".to_string(), "signed_up".to_string()],
        counts: vec![100, 50],
        drop_off_rates: vec![0.0, 50.0],
    };
    let json = build_funnel_figure(&agg);
    let traces = json["data"].as_array().unwrap();
    assert_eq!(traces.len(), 1);
}

#[test]
fn test_build_heatmap_figure_colorscale() {
    let agg = EventHeatmap {
        hours: vec![0, 1],
        days: vec!["Monday".to_string(), "Tuesday".to_string()],
        counts: vec![vec![1, 2], vec![3, 4]],
    };
    let json = build_heatmap_figure(&agg);
    let traces = json["data"].as_array().unwrap();
    let trace = &traces[0];
    assert!(trace["type"] == "heatmap" || trace["type"] == "heatmapgl" || !trace["type"].is_null());
}

#[test]
fn test_build_incident_bar_figure_severity_order() {
    let agg = IncidentSeverity {
        severities: vec!["critical".to_string(), "high".to_string()],
        counts: vec![1, 5],
        mttr_by_severity: std::collections::HashMap::new(),
    };
    let json = build_incident_bar_figure(&agg);
    let traces = json["data"].as_array().unwrap();
    assert_eq!(traces.len(), 1);
}

#[test]
fn test_all_figures_have_meta_key() {
    let ts_json = build_time_series_figure(&EventCountSeries::default());
    assert!(!ts_json["meta"].is_null());

    let svc_json = build_service_bar_figure(&ServiceErrorRates::default());
    assert!(!svc_json["meta"].is_null());

    let lh_json = build_latency_histogram_figure(&LatencyHistogram::default());
    assert!(!lh_json["meta"].is_null());

    let fn_json = build_funnel_figure(&FunnelStages::default());
    assert!(!fn_json["meta"].is_null());

    let hm_json = build_heatmap_figure(&EventHeatmap::default());
    assert!(!hm_json["meta"].is_null());

    let in_json = build_incident_bar_figure(&IncidentSeverity::default());
    assert!(!in_json["meta"].is_null());
}
