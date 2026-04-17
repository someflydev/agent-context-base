use super::to_figure_json;
use crate::analytics::EventCountSeries;
use plotly::common::{Mode, Title};
use plotly::{Plot, Scatter};
use serde_json::Value;

pub fn build_time_series_figure(agg: &EventCountSeries) -> Value {
    let mut plot = Plot::new();

    if agg.dates.is_empty() {
        let trace = Scatter::new(Vec::<String>::new(), Vec::<i64>::new()).mode(Mode::LinesMarkers);
        plot.add_trace(trace);
        let layout = plotly::Layout::new().title(Title::with_text("No data for selected filters"));
        plot.set_layout(layout);
        return to_figure_json(&plot, 0, true); // Assuming filtered if empty, doesn't matter much
    }

    let mut keys: Vec<String> = agg.by_environment.keys().cloned().collect();
    keys.sort();

    let mut total_count = 0;

    for env in keys {
        let counts = agg.by_environment.get(&env).unwrap().clone();
        let sum: i64 = counts.iter().sum();
        total_count += sum;

        let trace = Scatter::new(agg.dates.clone(), counts)
            .name(&env)
            .mode(Mode::LinesMarkers)
            .hover_template("%{x}<br>Environment: %{data.name}<br>Count: %{y}<extra></extra>");
        plot.add_trace(trace);
    }

    let layout = plotly::Layout::new()
        .title(Title::with_text("Event Count Over Time"))
        .x_axis(plotly::layout::Axis::new().title(Title::with_text("Date")))
        .y_axis(plotly::layout::Axis::new().title(Title::with_text("Count")));
    plot.set_layout(layout);

    to_figure_json(&plot, total_count, true)
}
