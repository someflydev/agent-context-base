use super::to_figure_json;
use crate::analytics::EventHeatmap;
use plotly::common::{Title, ColorScalePalette};
use plotly::{HeatMap, Plot};
use serde_json::Value;

pub fn build_heatmap_figure(agg: &EventHeatmap) -> Value {
    let mut plot = Plot::new();

    if agg.counts.is_empty() || agg.counts[0].is_empty() {
        let trace = HeatMap::new(vec![0.0], vec![0.0], vec![vec![0.0]]);
        plot.add_trace(trace);
        let layout = plotly::Layout::new().title(Title::with_text("No data for selected filters"));
        plot.set_layout(layout);
        return to_figure_json(&plot, 0, true);
    }

    // counts is 7 days x 24 hours. HeatMap takes Z as Vec<Vec<N>>
    let mut z_data = Vec::new();
    for day_row in &agg.counts {
        let mut row_f64 = Vec::new();
        for &val in day_row {
            row_f64.push(val as f64);
        }
        z_data.push(row_f64);
    }

    let total_count: i64 = agg.counts.iter().map(|row| row.iter().sum::<i64>()).sum();

    // HeatMap X is hours, Y is days
    let trace = HeatMap::new(agg.hours.clone(), agg.days.clone(), z_data)
        .color_scale(ColorScalePalette::Blues.into());
    
    plot.add_trace(trace);

    let layout = plotly::Layout::new()
        .title(Title::with_text("Activity Heatmap"))
        .x_axis(plotly::layout::Axis::new().title(Title::with_text("Hour of Day")))
        .y_axis(plotly::layout::Axis::new().title(Title::with_text("Day of Week")));
    plot.set_layout(layout);

    to_figure_json(&plot, total_count, true)
}