from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os

from ..data.loader import get_dataset
from ..filters import parse_filter_state, FilterState
from ..analytics.events import aggregate_event_counts
from ..analytics.services import aggregate_service_error_rates
from ..analytics.distributions import aggregate_latency_histogram, aggregate_latency_by_service
from ..analytics.incidents import aggregate_incident_severity
from ..analytics.funnel import aggregate_funnel_stages
from ..analytics.heatmap import aggregate_event_heatmap

from ..charts.time_series import build_time_series_figure
from ..charts.service_bar import build_service_bar_figure
from ..charts.latency_histogram import build_latency_histogram_figure
from ..charts.latency_boxplot import build_latency_boxplot_figure
from ..charts.incident_bar import build_incident_bar_figure
from ..charts.funnel_chart import build_funnel_figure
from ..charts.heatmap_chart import build_heatmap_figure

router = APIRouter()

# Setup templates
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

def get_base_context(request: Request, filters: FilterState, view_name: str):
    data = get_dataset()
    services_list = [{"id": s.name, "name": s.name} for s in data.services]
    env_set = set()
    for e in data.events:
        env_set.add(e.environment)
    environments_list = [{"id": e, "name": e} for e in sorted(list(env_set))]
    severity_levels_list = [{"id": s, "name": s} for s in ["critical", "high", "medium", "low"]]
    
    return {
        "request": request,
        "view_name": view_name,
        "services_list": services_list,
        "environments_list": environments_list,
        "severity_levels_list": severity_levels_list,
        "active_filters": {
            "date_from": filters.date_from.isoformat() if filters.date_from else "",
            "date_to": filters.date_to.isoformat() if filters.date_to else "",
            "services": filters.services,
            "severity": filters.severity,
            "environment": filters.environment
        },
        "fixture_info": {"profile": "smoke", "seed": 42}
    }

@router.get("/")
@router.get("/trends")
async def trends_view(request: Request, filters: FilterState = Depends(parse_filter_state)):
    data = get_dataset()
    agg = aggregate_event_counts(data.events, filters)
    fig_dict = build_time_series_figure(agg)
    
    summary = {
        "total_events": fig_dict["meta"]["total_count"],
        "date_range": f"{filters.date_from} to {filters.date_to}" if filters.date_from and filters.date_to else "All time"
    }
    
    ctx = get_base_context(request, filters, "Trends")
    ctx.update({"figure_json": json.dumps(fig_dict), "summary": summary})
    return templates.TemplateResponse(request=request, name="trends.html", context=ctx)

@router.get("/services")
async def services_view(request: Request, filters: FilterState = Depends(parse_filter_state)):
    data = get_dataset()
    agg = aggregate_service_error_rates(data.events, data.services, filters)
    fig_dict = build_service_bar_figure(agg)
    
    summary = {
        "total_events": fig_dict["meta"]["total_count"],
        "date_range": "All time"
    }
    
    ctx = get_base_context(request, filters, "Services")
    ctx.update({"figure_json": json.dumps(fig_dict), "summary": summary})
    return templates.TemplateResponse(request=request, name="services.html", context=ctx)

@router.get("/distributions")
async def distributions_view(request: Request, filters: FilterState = Depends(parse_filter_state)):
    data = get_dataset()
    agg_hist = aggregate_latency_histogram(data.latency_samples, filters, data.services)
    fig_hist = build_latency_histogram_figure(agg_hist)
    
    agg_box = aggregate_latency_by_service(data.latency_samples, data.services, filters)
    fig_box = build_latency_boxplot_figure(agg_box)
    
    summary = {
        "total_samples": fig_hist["meta"]["total_count"],
        "p50": f"{agg_hist.p50:.1f}ms",
        "p95": f"{agg_hist.p95:.1f}ms",
        "p99": f"{agg_hist.p99:.1f}ms"
    }
    
    ctx = get_base_context(request, filters, "Distributions")
    ctx.update({
        "figure_json": json.dumps(fig_hist), 
        "figure_box_json": json.dumps(fig_box), 
        "summary": summary
    })
    return templates.TemplateResponse(request=request, name="distributions.html", context=ctx)

@router.get("/heatmap")
async def heatmap_view(request: Request, filters: FilterState = Depends(parse_filter_state)):
    data = get_dataset()
    agg = aggregate_event_heatmap(data.events, filters)
    fig_dict = build_heatmap_figure(agg)
    
    summary = {
        "total_events": fig_dict["meta"]["total_count"]
    }
    
    ctx = get_base_context(request, filters, "Heatmap")
    ctx.update({"figure_json": json.dumps(fig_dict), "summary": summary})
    return templates.TemplateResponse(request=request, name="heatmap.html", context=ctx)

@router.get("/funnel")
async def funnel_view(request: Request, filters: FilterState = Depends(parse_filter_state)):
    data = get_dataset()
    agg = aggregate_funnel_stages(data.sessions, filters, data.funnel_stages)
    fig_dict = build_funnel_figure(agg)
    
    if agg.counts and agg.counts[0] > 0:
        overall_conversion = agg.counts[-1] / agg.counts[0]
    else:
        overall_conversion = 0.0
        
    summary = {
        "total_sessions": fig_dict["meta"]["total_count"],
        "overall_conversion": f"{overall_conversion:.1%}"
    }
    
    ctx = get_base_context(request, filters, "Funnel")
    ctx.update({"figure_json": json.dumps(fig_dict), "summary": summary})
    return templates.TemplateResponse(request=request, name="funnel.html", context=ctx)

@router.get("/incidents")
async def incidents_view(request: Request, filters: FilterState = Depends(parse_filter_state)):
    data = get_dataset()
    agg = aggregate_incident_severity(data.incidents, filters, data.services)
    fig_dict = build_incident_bar_figure(agg)
    
    summary = {
        "total_incidents": fig_dict["meta"]["total_count"],
        "mttr_by_severity": agg.mttr_by_severity
    }
    
    ctx = get_base_context(request, filters, "Incidents")
    ctx.update({"figure_json": json.dumps(fig_dict), "summary": summary})
    return templates.TemplateResponse(request=request, name="incidents.html", context=ctx)
