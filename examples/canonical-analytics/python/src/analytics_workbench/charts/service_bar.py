import plotly.graph_objects as go
from ..analytics.services import ServiceErrorRates
from datetime import datetime

def build_service_bar_figure(agg: ServiceErrorRates) -> dict:
    fig = go.Figure()
    
    total_count = sum(agg.total_events) if agg.total_events else 0
    
    if not agg.services:
        fig.add_annotation(text="No data available", showarrow=False, font=dict(size=20))
        fig.update_layout(title_text="Service Error Rates", xaxis_title_text="Error Rate", yaxis_title_text="Service")
    else:
        # We need horizontal sorted bar, sorted descending by error rate
        # Plotly draws horizontal bars from bottom up, so to show highest at top we reverse the lists
        services_rev = agg.services[::-1]
        rates_rev = agg.error_rates[::-1]
        
        fig.add_trace(go.Bar(
            x=rates_rev,
            y=services_rev,
            orientation="h",
            name="Error Rate",
            hovertemplate="Service: %{y}<br>Error Rate: %{x:.2%}<extra></extra>"
        ))
        
        fig.update_layout(
            title_text="Service Error Rates",
            xaxis_title_text="Error Rate",
            yaxis_title_text="Service",
            xaxis_tickformat=".0%"
        )
        
    fig_dict = fig.to_dict()
    fig_dict["meta"] = {
        "total_count": total_count,
        "filters_applied": [],
        "generated_at": datetime.utcnow().isoformat()
    }
    return fig_dict
