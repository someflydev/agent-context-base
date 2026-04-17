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
use std::sync::Arc;

#[derive(Template)]
#[template(path = "trends.html")]
pub struct TrendsTemplate {
    pub figure_json: String,
    pub view_name: String,
}

#[derive(Template)]
#[template(path = "services.html")]
pub struct ServicesTemplate {
    pub figure_json: String,
    pub view_name: String,
}

#[derive(Template)]
#[template(path = "distributions.html")]
pub struct DistributionsTemplate {
    pub figure_json_a: String,
    pub figure_json_b: String,
    pub view_name: String,
}

#[derive(Template)]
#[template(path = "heatmap.html")]
pub struct HeatmapTemplate {
    pub figure_json: String,
    pub view_name: String,
}

#[derive(Template)]
#[template(path = "funnel.html")]
pub struct FunnelTemplate {
    pub figure_json: String,
    pub view_name: String,
}

#[derive(Template)]
#[template(path = "incidents.html")]
pub struct IncidentsTemplate {
    pub figure_json: String,
    pub view_name: String,
}

#[derive(Template)]
#[template(path = "index.html")]
pub struct IndexTemplate {
    pub trends_figure_json: String,
    pub services_figure_json: String,
    pub view_name: String,
}

pub async fn index(
    State(store): State<Arc<FixtureStore>>,
    Query(filters): Query<FilterState>,
) -> impl IntoResponse {
    let agg_trends = aggregate_events(&store.events, &filters);
    let fig_trends = build_time_series_figure(&agg_trends);

    let agg_services = aggregate_services(&store.services, &store.events, &filters);
    let fig_services = build_service_bar_figure(&agg_services);

    IndexTemplate {
        trends_figure_json: fig_trends.to_string(),
        services_figure_json: fig_services.to_string(),
        view_name: "overview".to_string(),
    }
}

pub async fn trends(
    State(store): State<Arc<FixtureStore>>,
    Query(filters): Query<FilterState>,
) -> impl IntoResponse {
    let agg = aggregate_events(&store.events, &filters);
    let fig = build_time_series_figure(&agg);

    TrendsTemplate {
        figure_json: fig.to_string(),
        view_name: "trends".to_string(),
    }
}

pub async fn services(
    State(store): State<Arc<FixtureStore>>,
    Query(filters): Query<FilterState>,
) -> impl IntoResponse {
    let agg = aggregate_services(&store.services, &store.events, &filters);
    let fig = build_service_bar_figure(&agg);

    ServicesTemplate {
        figure_json: fig.to_string(),
        view_name: "services".to_string(),
    }
}

pub async fn distributions(
    State(store): State<Arc<FixtureStore>>,
    Query(filters): Query<FilterState>,
) -> impl IntoResponse {
    let agg_a = aggregate_latency_histogram(&store.latency_samples, &filters);
    let fig_a = build_latency_histogram_figure(&agg_a);

    let agg_b = aggregate_latency_by_service(&store.latency_samples, &filters);
    let fig_b = build_latency_boxplot_figure(&agg_b);

    DistributionsTemplate {
        figure_json_a: fig_a.to_string(),
        figure_json_b: fig_b.to_string(),
        view_name: "distributions".to_string(),
    }
}

pub async fn heatmap(
    State(store): State<Arc<FixtureStore>>,
    Query(filters): Query<FilterState>,
) -> impl IntoResponse {
    let agg = aggregate_event_heatmap(&store.events, &filters);
    let fig = build_heatmap_figure(&agg);

    HeatmapTemplate {
        figure_json: fig.to_string(),
        view_name: "heatmap".to_string(),
    }
}

pub async fn funnel(
    State(store): State<Arc<FixtureStore>>,
    Query(filters): Query<FilterState>,
) -> impl IntoResponse {
    let agg = aggregate_funnel_stages(&store.sessions, &store.funnel_stages, &filters);
    let fig = build_funnel_figure(&agg);

    FunnelTemplate {
        figure_json: fig.to_string(),
        view_name: "funnel".to_string(),
    }
}

pub async fn incidents(
    State(store): State<Arc<FixtureStore>>,
    Query(filters): Query<FilterState>,
) -> impl IntoResponse {
    let agg = aggregate_incident_severity(&store.incidents, &store.services, &filters);
    let fig = build_incident_bar_figure(&agg);

    IncidentsTemplate {
        figure_json: fig.to_string(),
        view_name: "incidents".to_string(),
    }
}
