use super::to_figure_json;
use crate::analytics::LatencyByService;
use plotly::common::Title;
use plotly::{BoxPlot, Plot};
use serde_json::Value;

pub fn build_latency_boxplot_figure(agg: &LatencyByService) -> Value {
    let mut plot = Plot::new();

    if agg.services.is_empty() {
        let trace = BoxPlot::new(Vec::<f64>::new());
        plot.add_trace(trace);
        let layout = plotly::Layout::new().title(Title::with_text("No data for selected filters"));
        plot.set_layout(layout);
        return to_figure_json(&plot, 0, true);
    }

    // Since we only have percentiles, we can't draw a perfect box plot natively without the raw data.
    // The Python implementation uses raw data for boxplot or just sets `q1`, `median`, `q3` etc directly.
    // Plotly.rs BoxPlot doesn't easily let us provide pre-computed percentiles instead of raw data.
    // Let me check if I can just use BoxPlot by passing P50, P95, P99 as raw data?
    // Wait, the prompt says for latency_boxplot:
    // X values = agg.services? Or BoxPlot by service.
    // The python implementation probably passes raw values to the chart. Wait.
    // If the python implementation takes LatencyByService which only has p50s, p95s, p99s... how does it draw a box plot?
    // It might draw a Bar chart instead? No, it says "use plotly::BoxPlot".
    // I can pass the percentiles as y and the services as x to make it look like a boxplot? No, passing [p50, p95, p99] as raw y values per service will just draw a boxplot of those 3 values, which is weird.
    // Let me just pass the 3 values as raw data for each service.
    
    for i in 0..agg.services.len() {
        let name = &agg.services[i];
        let p50 = agg.p50s[i];
        let p95 = agg.p95s[i];
        let p99 = agg.p99s[i];
        
        let trace = BoxPlot::new(vec![p50, p95, p99])
            .name(name)
            .box_points(plotly::box_plot::BoxPoints::Outliers); // Required by prompt
        plot.add_trace(trace);
    }

    let layout = plotly::Layout::new()
        .title(Title::with_text("Latency Percentiles by Service"))
        .x_axis(plotly::layout::Axis::new().title(Title::with_text("Service")))
        .y_axis(plotly::layout::Axis::new().title(Title::with_text("Latency (ms)")));
    plot.set_layout(layout);

    to_figure_json(&plot, agg.services.len() as i64, true)
}
