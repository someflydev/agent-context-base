use super::to_figure_json;
use crate::analytics::FunnelStages;
use plotly::common::Title;
use plotly::{Bar, Plot};
use serde_json::Value;

pub fn build_funnel_figure(agg: &FunnelStages) -> Value {
    let mut plot = Plot::new();

    if agg.stages.is_empty() {
        let trace = Bar::new(Vec::<String>::new(), Vec::<i64>::new());
        plot.add_trace(trace);
        let layout = plotly::Layout::new().title(Title::with_text("No data for selected filters"));
        plot.set_layout(layout);
        return to_figure_json(&plot, 0, true);
    }

    // plotly.rs does not have a Funnel trace type in 0.10.0 natively easily accessible,
    // so the prompt says: "If plotly.rs does not have a Funnel type in the version you are using, 
    // use Bar with text annotations for drop-off. Document the substitution clearly."

    let total_count: i64 = *agg.counts.first().unwrap_or(&0);

    let mut text_annotations = Vec::new();
    for drop in &agg.drop_off_rates {
        text_annotations.push(format!("{:.1}% drop", drop * 100.0));
    }

    let trace = Bar::new(agg.stages.clone(), agg.counts.clone())
        .text_array(text_annotations)
        .hover_template("Stage: %{x}<br>Count: %{y}<extra></extra>");
    
    plot.add_trace(trace);

    let layout = plotly::Layout::new()
        .title(Title::with_text("Session Funnel"))
        .x_axis(plotly::layout::Axis::new().title(Title::with_text("Stage")))
        .y_axis(plotly::layout::Axis::new().title(Title::with_text("Count")));
    plot.set_layout(layout);

    to_figure_json(&plot, total_count, true)
}
