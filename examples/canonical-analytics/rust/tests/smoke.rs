use axum::{routing::get, Router};
use std::sync::Arc;
use axum_test::TestServer;

use analytics_workbench_rust::data::loader::{get_fixture_path, load_fixtures};
use analytics_workbench_rust::handlers::{fragments, health, pages};

fn app() -> Router {
    let fixture_path = get_fixture_path();
    let store = Arc::new(load_fixtures(&fixture_path).unwrap());

    Router::new()
        .route("/health", get(health::health))
        .route("/", get(pages::index))
        .route("/trends", get(pages::trends))
        .route("/services", get(pages::services))
        .route("/distributions", get(pages::distributions))
        .route("/heatmap", get(pages::heatmap))
        .route("/funnel", get(pages::funnel))
        .route("/incidents", get(pages::incidents))
        .route("/fragments/chart", get(fragments::fragment_chart))
        .route("/fragments/summary", get(fragments::fragment_summary))
        .route("/fragments/details", get(fragments::fragment_details))
        .with_state(store)
}

#[tokio::test]
async fn test_health_returns_ok() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/health").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_index_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_trends_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/trends").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_services_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/services").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_distributions_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/distributions").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_heatmap_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/heatmap").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_funnel_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/funnel").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_incidents_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/incidents").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_fragment_chart_trends_returns_200_with_plotly() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/fragments/chart").add_query_param("view", "trends").await;
    response.assert_status_ok();
    let text = response.text();
    assert!(text.contains("data-figure") || text.contains("plotly"));
}

#[tokio::test]
async fn test_fragment_summary_trends_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/fragments/summary").add_query_param("view", "trends").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_fragment_details_services_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/fragments/details").add_query_param("service", "web").await;
    response.assert_status_ok();
}

#[tokio::test]
async fn test_filter_by_environment_returns_200() {
    let server = TestServer::new(app()).unwrap();
    let response = server.get("/trends").add_query_param("environment", "production").await;
    response.assert_status_ok();
}
