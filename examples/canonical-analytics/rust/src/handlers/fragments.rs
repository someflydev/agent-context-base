use crate::analytics::{
    distributions::{aggregate_latency_by_service, aggregate_latency_histogram},
    events::aggregate_events,
    funnel::aggregate_funnel_stages,
    heatmap::aggregate_event_heatmap,
    incidents::aggregate_incident_severity,
    services::aggregate_services,
};
use crate::charts::{
    funnel_chart::build_funnel_figure,
    heatmap_chart::build_heatmap_figure,
    incident_bar::build_incident_bar_figure,
    latency_boxplot::build_latency_boxplot_figure,
    latency_histogram::build_latency_histogram_figure,
    service_bar::build_service_bar_figure,
    time_series::build_time_series_figure,
};
use crate::data::loader::FixtureStore;
use crate::filters::FilterState;
use askama::Template;
use axum::{
    extract::{Query, State},
    response::IntoResponse,
};
use serde::Deserialize;
use std::sync::Arc;

#[derive(Debug, Deserialize)]
pub struct FragmentQuery {
    pub view: Option<String>,
    pub service: Option<String>,
    #[serde(flatten)]
    pub filters: FilterState,
}

#[derive(Template)]
#[template(path = "fragments/chart.html")]
pub struct ChartFragment {
    pub figure_json: String,
    pub figure_json_b: Option<String>, // For distributions where we have two charts
}

#[derive(Template)]
#[template(path = "fragments/summary.html")]
pub struct SummaryFragment {
    pub total_count: i64,
    pub extra_info: String,
}

#[derive(Template)]
#[template(path = "fragments/details.html")]
pub struct DetailsFragment {
    pub service_name: String,
    pub top_incidents: Vec<crate::data::models::Incident>,
}

pub async fn fragment_chart(
    State(store): State<Arc<FixtureStore>>,
    Query(query): Query<FragmentQuery>,
) -> impl IntoResponse {
    let mut figure_json_b = None;
    let figure_json = match query.view.as_deref().unwrap_or("") {
        "trends" => {
            let agg = aggregate_events(&store.events, &query.filters);
            let fig = build_time_series_figure(&agg);
            fig.to_string()
        }
        "services" => {
            let agg = aggregate_services(&store.services, &store.events, &query.filters);
            let fig = build_service_bar_figure(&agg);
            fig.to_string()
        }
        "distributions" => {
            let agg_a = aggregate_latency_histogram(&store.latency_samples, &query.filters);
            let fig_a = build_latency_histogram_figure(&agg_a);
            
            let agg_b = aggregate_latency_by_service(&store.latency_samples, &query.filters);
            let fig_b = build_latency_boxplot_figure(&agg_b);
            figure_json_b = Some(fig_b.to_string());
            
            fig_a.to_string()
        }
        "heatmap" => {
            let agg = aggregate_event_heatmap(&store.events, &query.filters);
            let fig = build_heatmap_figure(&agg);
            fig.to_string()
        }
        "funnel" => {
            let agg = aggregate_funnel_stages(&store.sessions, &store.funnel_stages, &query.filters);
            let fig = build_funnel_figure(&agg);
            fig.to_string()
        }
        "incidents" => {
            let agg = aggregate_incident_severity(&store.incidents, &store.services, &query.filters);
            let fig = build_incident_bar_figure(&agg);
            fig.to_string()
        }
        _ => "{}".to_string(),
    };

    ChartFragment {
        figure_json,
        figure_json_b,
    }
}

pub async fn fragment_summary(
    State(store): State<Arc<FixtureStore>>,
    Query(query): Query<FragmentQuery>,
) -> impl IntoResponse {
    let mut total_count = 0;
    let mut extra_info = String::new();

    match query.view.as_deref().unwrap_or("") {
        "trends" => {
            let agg = aggregate_events(&store.events, &query.filters);
            total_count = agg.counts.iter().sum();
            extra_info = "Events shown".to_string();
        }
        "services" => {
            let agg = aggregate_services(&store.services, &store.events, &query.filters);
            total_count = agg.total_events.iter().sum();
            extra_info = "Services shown".to_string();
        }
        "distributions" => {
            let agg = aggregate_latency_histogram(&store.latency_samples, &query.filters);
            total_count = agg.values.len() as i64;
            extra_info = format!("P50: {:.2}ms, P95: {:.2}ms", agg.p50, agg.p95);
        }
        "heatmap" => {
            let agg = aggregate_event_heatmap(&store.events, &query.filters);
            total_count = agg.counts.iter().map(|row| row.iter().sum::<i64>()).sum();
            extra_info = "Heatmap activity".to_string();
        }
        "funnel" => {
            let agg = aggregate_funnel_stages(&store.sessions, &store.funnel_stages, &query.filters);
            total_count = *agg.counts.first().unwrap_or(&0);
            extra_info = "Initial sessions".to_string();
        }
        "incidents" => {
            let agg = aggregate_incident_severity(&store.incidents, &store.services, &query.filters);
            total_count = agg.counts.iter().sum();
            extra_info = "Total incidents".to_string();
        }
        _ => {}
    }

    SummaryFragment {
        total_count,
        extra_info,
    }
}

pub async fn fragment_details(
    State(store): State<Arc<FixtureStore>>,
    Query(query): Query<FragmentQuery>,
) -> impl IntoResponse {
    let srv_name = query.service.unwrap_or_default();
    let mut top_incidents = Vec::new();
    
    for i in &store.incidents {
        if i.service == srv_name {
            top_incidents.push(i.clone());
        }
    }
    
    top_incidents.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
    top_incidents.truncate(5);

    DetailsFragment {
        service_name: srv_name,
        top_incidents,
    }
}
