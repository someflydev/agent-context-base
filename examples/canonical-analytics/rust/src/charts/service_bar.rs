use super::to_figure_json;
use crate::analytics::ServiceErrorRates;
use plotly::common::{Orientation, Title};
use plotly::{Bar, Plot};
use serde_json::Value;

pub fn build_service_bar_figure(agg: &ServiceErrorRates) -> Value {
    let mut plot = Plot::new();

    if agg.services.is_empty() {
        let trace = Bar::new(Vec::<f64>::new(), Vec::<String>::new()).orientation(Orientation::Horizontal);
        plot.add_trace(trace);
        let layout = plotly::Layout::new().title(Title::with_text("No data for selected filters"));
        plot.set_layout(layout);
        return to_figure_json(&plot, 0, true);
    }

    // Sort ascending for Plotly horizontal bar so top is at the top
    let mut srvs = agg.services.clone();
    srvs.reverse();
    let mut rates = agg.error_rates.clone();
    rates.reverse();
    
    let total_count: i64 = agg.total_events.iter().sum();

    let trace = Bar::new(rates, srvs)
        .orientation(Orientation::Horizontal)
        .hover_template("Service: %{y}<br>Error Rate: %{x:.2%}<extra></extra>");
    
    plot.add_trace(trace);

    let layout = plotly::Layout::new()
        .title(Title::with_text("Service Error Rates"))
        .x_axis(plotly::layout::Axis::new().title(Title::with_text("Error Rate")))
        .y_axis(plotly::layout::Axis::new().title(Title::with_text("Service")));
    plot.set_layout(layout);

    to_figure_json(&plot, total_count, true)
}
