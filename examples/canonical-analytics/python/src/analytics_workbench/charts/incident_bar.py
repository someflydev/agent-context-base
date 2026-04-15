import plotly.graph_objects as go
from ..analytics.incidents import IncidentSeverity
from datetime import datetime

def build_incident_bar_figure(agg: IncidentSeverity) -> dict:
    fig = go.Figure()
    
    total_count = sum(agg.counts) if agg.counts else 0
    
    if not agg.severities:
        fig.add_annotation(text="No data available", showarrow=False, font=dict(size=20))
        fig.update_layout(title_text="Incident Count by Severity", xaxis_title_text="Severity", yaxis_title_text="Count")
    else:
        fig.add_trace(go.Bar(
            x=agg.severities,
            y=agg.counts,
            name="Incidents",
            hovertemplate="Severity: %{x}<br>Count: %{y}<extra></extra>"
        ))
        
        fig.update_layout(
            title_text="Incident Count by Severity",
            xaxis_title_text="Severity",
            yaxis_title_text="Count"
        )
        
    fig_dict = fig.to_dict()
    fig_dict["meta"] = {
        "total_count": total_count,
        "filters_applied": [],
        "generated_at": datetime.utcnow().isoformat()
    }
    return fig_dict
