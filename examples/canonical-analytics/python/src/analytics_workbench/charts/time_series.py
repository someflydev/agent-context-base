import plotly.graph_objects as go
from ..analytics.events import EventCountSeries
from datetime import datetime

def build_time_series_figure(agg: EventCountSeries) -> dict:
    fig = go.Figure()
    
    total_count = sum(agg.counts) if agg.counts else 0
    
    if not agg.dates:
        # Empty state
        fig.add_annotation(text="No data available", showarrow=False, font=dict(size=20))
        fig.update_layout(title_text="Event Trends over Time", xaxis_title_text="Date", yaxis_title_text="Count")
    else:
        for env, counts in agg.by_environment.items():
            fig.add_trace(go.Scatter(
                x=agg.dates,
                y=counts,
                mode="lines+markers",
                name=env,
                hovertemplate=f"Date: %{{x}}<br>{env} Events: %{{y}}<extra></extra>"
            ))
            
        fig.update_layout(
            title_text="Event Trends over Time",
            xaxis_title_text="Date",
            yaxis_title_text="Count"
        )
        
    fig_dict = fig.to_dict()
    fig_dict["meta"] = {
        "total_count": total_count,
        "filters_applied": [],
        "generated_at": datetime.utcnow().isoformat()
    }
    return fig_dict
