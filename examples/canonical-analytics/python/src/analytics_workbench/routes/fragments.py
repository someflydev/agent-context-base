from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
import os

from ..data.loader import get_dataset
from ..filters import parse_filter_state, FilterState
from .pages import (
    get_base_context,
    aggregate_event_counts, build_time_series_figure,
    aggregate_service_error_rates, build_service_bar_figure,
    aggregate_latency_histogram, build_latency_histogram_figure,
    aggregate_incident_severity, build_incident_bar_figure,
    aggregate_funnel_stages, build_funnel_figure,
    aggregate_event_heatmap, build_heatmap_figure
)

router = APIRouter(prefix="/fragments")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

def get_view_data(view: str, filters: FilterState):
    data = get_dataset()
    v = view.lower()
    if v == "trends":
        agg = aggregate_event_counts(data.events, filters)
        fig = build_time_series_figure(agg)
        summary = {"total_events": fig["meta"]["total_count"]}
        return fig, summary
    elif v == "services":
        agg = aggregate_service_error_rates(data.events, data.services, filters)
        fig = build_service_bar_figure(agg)
        summary = {"total_events": fig["meta"]["total_count"]}
        return fig, summary
    elif v == "distributions":
        agg = aggregate_latency_histogram(data.latency_samples, filters, data.services)
        fig = build_latency_histogram_figure(agg)
        summary = {"total_samples": fig["meta"]["total_count"]}
        return fig, summary
    elif v == "heatmap":
        agg = aggregate_event_heatmap(data.events, filters)
        fig = build_heatmap_figure(agg)
        summary = {"total_events": fig["meta"]["total_count"]}
        return fig, summary
    elif v == "funnel":
        agg = aggregate_funnel_stages(data.sessions, filters, data.funnel_stages)
        fig = build_funnel_figure(agg)
        summary = {"total_sessions": fig["meta"]["total_count"]}
        return fig, summary
    elif v == "incidents":
        agg = aggregate_incident_severity(data.incidents, filters, data.services)
        fig = build_incident_bar_figure(agg)
        summary = {"total_incidents": fig["meta"]["total_count"]}
        return fig, summary
    else:
        raise HTTPException(status_code=400, detail="Unknown view")

@router.get("/chart")
async def fragment_chart(request: Request, view: str = "Trends", filters: FilterState = Depends(parse_filter_state)):
    fig, _ = get_view_data(view, filters)
    return templates.TemplateResponse(request=request, name="fragments/chart.html", context={
        "request": request,
        "figure_json": json.dumps(fig)
    })

@router.get("/summary")
async def fragment_summary(request: Request, view: str = "Trends", filters: FilterState = Depends(parse_filter_state)):
    _, summary = get_view_data(view, filters)
    return templates.TemplateResponse(request=request, name="fragments/summary.html", context={
        "request": request,
        "summary": summary,
        "active_filters": filters.__dict__
    })

@router.get("/details")
async def fragment_details(request: Request, view: str = "Services", service: str = "", filters: FilterState = Depends(parse_filter_state)):
    data = get_dataset()
    if view.lower() == "services":
        # top 5 recent incidents for service
        incs = [i for i in data.incidents if i.service == service]
        incs.sort(key=lambda x: x.timestamp, reverse=True)
        top5 = incs[:5]
        return templates.TemplateResponse(request=request, name="fragments/details.html", context={
            "request": request,
            "details": top5,
            "service_name": service
        })
    return HTMLResponse("")
