import plotly.graph_objects as go
from ..analytics.distributions import LatencyHistogram
from datetime import datetime

def build_latency_histogram_figure(agg: LatencyHistogram) -> dict:
    fig = go.Figure()
    
    total_count = len(agg.values)
    
    if not agg.values:
        fig.add_annotation(text="No data available", showarrow=False, font=dict(size=20))
        fig.update_layout(title_text="Latency Distribution", xaxis_title_text="Latency (ms)", yaxis_title_text="Count")
    else:
        fig.add_trace(go.Histogram(
            x=agg.values,
            xbins=dict(size=agg.bin_size),
            name="Latency",
            hovertemplate="Latency: %{x} ms<br>Count: %{y}<extra></extra>"
        ))
        
        fig.add_vline(x=agg.p50, line_dash="dash", line_color="red", annotation_text=f"P50: {agg.p50:.1f}ms")
        
        fig.update_layout(
            title_text="Latency Distribution",
            xaxis_title_text="Latency (ms)",
            yaxis_title_text="Count"
        )
        
    fig_dict = fig.to_dict()
    fig_dict["meta"] = {
        "total_count": total_count,
        "filters_applied": [],
        "generated_at": datetime.utcnow().isoformat()
    }
    return fig_dict
