use super::to_figure_json;
use crate::analytics::LatencyHistogram;
use plotly::common::Title;
use plotly::{Histogram, Plot};
use serde_json::Value;

pub fn build_latency_histogram_figure(agg: &LatencyHistogram) -> Value {
    let mut plot = Plot::new();

    if agg.values.is_empty() {
        let trace = Histogram::new(Vec::<f64>::new());
        plot.add_trace(trace);
        let layout = plotly::Layout::new().title(Title::with_text("No data for selected filters"));
        plot.set_layout(layout);
        return to_figure_json(&plot, 0, true);
    }

    let trace = Histogram::new(agg.values.clone())
        .name("Latency")
        .hover_template("Latency: %{x}ms<br>Count: %{y}<extra></extra>");
    plot.add_trace(trace);

    let shape = plotly::layout::Shape::new()
        .shape_type(plotly::layout::ShapeType::Line)
        .x0(agg.p50)
        .x1(agg.p50)
        .y0(0.0)
        .y1(1.0)
        .y_ref("paper")
        .line(plotly::layout::ShapeLine::new().color("red").width(2.0).dash(plotly::common::DashType::Dash));

    let layout = plotly::Layout::new()
        .title(Title::with_text(format!("Latency Distribution (P50: {:.2}ms)", agg.p50)))
        .x_axis(plotly::layout::Axis::new().title(Title::with_text("Latency (ms)")))
        .y_axis(plotly::layout::Axis::new().title(Title::with_text("Count")))
        .shapes(vec![shape]);
    plot.set_layout(layout);

    to_figure_json(&plot, agg.values.len() as i64, true)
}
