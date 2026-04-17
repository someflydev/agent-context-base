use super::to_figure_json;
use crate::analytics::IncidentSeverity;
use plotly::common::Title;
use plotly::{Bar, Plot};
use serde_json::Value;

pub fn build_incident_bar_figure(agg: &IncidentSeverity) -> Value {
    let mut plot = Plot::new();

    if agg.severities.is_empty() {
        let trace = Bar::new(Vec::<String>::new(), Vec::<i64>::new());
        plot.add_trace(trace);
        let layout = plotly::Layout::new().title(Title::with_text("No data for selected filters"));
        plot.set_layout(layout);
        return to_figure_json(&plot, 0, true);
    }

    let total_count: i64 = agg.counts.iter().sum();

    let trace = Bar::new(agg.severities.clone(), agg.counts.clone())
        .hover_template("Severity: %{x}<br>Count: %{y}<extra></extra>");
    plot.add_trace(trace);

    let layout = plotly::Layout::new()
        .title(Title::with_text("Incidents by Severity"))
        .x_axis(plotly::layout::Axis::new().title(Title::with_text("Severity")))
        .y_axis(plotly::layout::Axis::new().title(Title::with_text("Count")));
    plot.set_layout(layout);

    to_figure_json(&plot, total_count, true)
}
