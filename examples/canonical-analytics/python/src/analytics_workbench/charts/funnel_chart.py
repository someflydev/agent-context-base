import plotly.graph_objects as go
from ..analytics.funnel import FunnelStages
from datetime import datetime

def build_funnel_figure(agg: FunnelStages) -> dict:
    fig = go.Figure()
    
    total_count = agg.counts[0] if agg.counts else 0
    
    if not agg.stages:
        fig.add_annotation(text="No data available", showarrow=False, font=dict(size=20))
        fig.update_layout(title_text="Session Funnel", xaxis_title_text="Count", yaxis_title_text="Stage")
    else:
        # Include drop-off percentage in hover text
        hover_texts = []
        for i in range(len(agg.stages)):
            pct = agg.drop_off_rates[i] * 100
            hover_texts.append(f"Drop-off: {pct:.1f}%")
            
        fig.add_trace(go.Funnel(
            y=agg.stages,
            x=agg.counts,
            name="Funnel",
            textinfo="value+percent initial",
            hovertext=hover_texts,
            hovertemplate="Stage: %{y}<br>Count: %{x}<br>%{hovertext}<extra></extra>"
        ))
        
        fig.update_layout(
            title_text="Session Funnel",
            xaxis_title_text="Count",
            yaxis_title_text="Stage"
        )
        
    fig_dict = fig.to_dict()
    fig_dict["meta"] = {
        "total_count": total_count,
        "filters_applied": [],
        "generated_at": datetime.utcnow().isoformat()
    }
    return fig_dict
