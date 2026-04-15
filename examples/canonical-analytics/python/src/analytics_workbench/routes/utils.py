import json
from typing import Tuple
from fastapi import Request
from ..filters import FilterState, parse_filter_state
from ..data.loader import get_dataset
from ..analytics.events import aggregate_event_counts
from ..analytics.services import aggregate_service_error_rates
from ..analytics.distributions import aggregate_latency_histogram, aggregate_latency_by_service
from ..analytics.heatmap import aggregate_event_heatmap
from ..analytics.funnel import aggregate_funnel_stages
from ..analytics.incidents import aggregate_incident_severity

from ..charts.time_series import build_time_series_figure
from ..charts.service_bar import build_service_bar_figure
from ..charts.latency_histogram import build_latency_histogram_figure
from ..charts.latency_boxplot import build_latency_boxplot_figure
from ..charts.heatmap_chart import build_heatmap_figure
from ..charts.funnel_chart import build_funnel_figure
from ..charts.incident_bar import build_incident_bar_figure

def get_view_data(view: str, filters: FilterState) -> Tuple[dict, dict]:
    dataset = get_dataset()
    
    figure_dict = {}
    summary = {
        "date_from": filters.date_from.isoformat() if filters.date_from else None,
        "date_to": filters.date_to.isoformat() if filters.date_to else None,
        "services": filters.services,
        "environment": filters.environment,
        "severity": filters.severity,
    }
    
    if view in ("trends", "home", "index", ""):
        agg = aggregate_event_counts(dataset.events, filters)
        figure_dict = build_time_series_figure(agg)
        
    elif view == "services":
        agg = aggregate_service_error_rates(dataset.events, dataset.services, filters)
        figure_dict = build_service_bar_figure(agg)
        
    elif view == "distributions":
        # For distributions, the spec is ambiguous whether to use histogram or boxplot by default in the main chart.
        # Usually we might render both or just histogram. Let's use latency histogram as the primary chart.
        agg = aggregate_latency_histogram(dataset.latency_samples, filters)
        figure_dict = build_latency_histogram_figure(agg)
        
    elif view == "heatmap":
        agg = aggregate_event_heatmap(dataset.events, filters)
        figure_dict = build_heatmap_figure(agg)
        
    elif view == "funnel":
        agg = aggregate_funnel_stages(dataset.sessions, filters)
        figure_dict = build_funnel_figure(agg)
        
    elif view == "incidents":
        agg = aggregate_incident_severity(dataset.incidents, filters)
        figure_dict = build_incident_bar_figure(agg)
        
    if figure_dict:
        summary["total_count"] = figure_dict.get("meta", {}).get("total_count", 0)
        
    return figure_dict, summary

def get_base_context(request: Request, view: str, filters: FilterState, figure_dict: dict, summary: dict) -> dict:
    dataset = get_dataset()
    
    services_list = list(set(s.name for s in dataset.services))
    environments_list = list(set(e.environment for e in dataset.events))
    severity_levels_list = list(set(inc.severity for inc in dataset.incidents))
    
    # Fill defaults if missing
    if not environments_list:
        environments_list = ["production", "staging"]
    if not severity_levels_list:
        severity_levels_list = ["low", "medium", "high", "critical"]
        
    return {
        "request": request,
        "view_name": view,
        "figure_json": json.dumps(figure_dict),
        "summary": summary,
        "active_filters": {
            "date_from": filters.date_from.isoformat() if filters.date_from else "",
            "date_to": filters.date_to.isoformat() if filters.date_to else "",
            "services": filters.services,
            "environment": filters.environment,
            "severity": filters.severity
        },
        "services_list": sorted(services_list),
        "environments_list": sorted(environments_list),
        "severity_levels_list": sorted(severity_levels_list)
    }
