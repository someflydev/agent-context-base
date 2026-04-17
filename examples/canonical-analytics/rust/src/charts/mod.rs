// Rust figure builders return serde_json::Value rather than a typed struct
// because plotly.rs's Plot type does not implement Clone or meaningful
// introspection. serde_json::Value is the structured form that handlers
// serialize to a response body, and test code can assert on JSON structure.
// This matches the spirit of the three-layer model: aggregation → builder →
// handler, with the builder returning a testable object.

pub mod funnel_chart;
pub mod heatmap_chart;
pub mod incident_bar;
pub mod latency_boxplot;
pub mod latency_histogram;
pub mod service_bar;
pub mod time_series;

use chrono::Utc;
use plotly::Plot;
use serde_json::Value;

pub fn to_figure_json(plot: &Plot, total_count: i64, filters_applied: bool) -> Value {
    let mut value = serde_json::to_value(plot).unwrap_or_default();
    value["meta"] = serde_json::json!({
        "total_count": total_count,
        "filters_applied": filters_applied,
        "generated_at": Utc::now().to_rfc3339()
    });
    value
}
