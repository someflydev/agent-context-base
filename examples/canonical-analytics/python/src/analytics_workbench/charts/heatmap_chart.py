import plotly.graph_objects as go
from ..analytics.heatmap import EventHeatmap
from datetime import datetime

def build_heatmap_figure(agg: EventHeatmap) -> dict:
    fig = go.Figure()
    
    total_count = sum(sum(row) for row in agg.counts) if agg.counts else 0
    
    if not agg.days:
        fig.add_annotation(text="No data available", showarrow=False, font=dict(size=20))
        fig.update_layout(title_text="Event Heatmap", xaxis_title_text="Hour of Day", yaxis_title_text="Day of Week")
    else:
        fig.add_trace(go.Heatmap(
            z=agg.counts,
            x=agg.hours,
            y=agg.days,
            colorscale="Blues",
            name="Heatmap",
            hovertemplate="Day: %{y}<br>Hour: %{x}<br>Count: %{z}<extra></extra>"
        ))
        
        fig.update_layout(
            title_text="Event Heatmap",
            xaxis_title_text="Hour of Day",
            yaxis_title_text="Day of Week"
        )
        
    fig_dict = fig.to_dict()
    fig_dict["meta"] = {
        "total_count": total_count,
        "filters_applied": [],
        "generated_at": datetime.utcnow().isoformat()
    }
    return fig_dict
