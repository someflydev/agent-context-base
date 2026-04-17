#![allow(dead_code)]
use axum::{routing::get, Router};
use std::sync::Arc;

use analytics_workbench_rust::data;
use analytics_workbench_rust::handlers;

use data::loader::{get_fixture_path, load_fixtures};
use handlers::{fragments, health, pages};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let fixture_path = get_fixture_path();
    let store = Arc::new(load_fixtures(&fixture_path)?);

    let app = Router::new()
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
        .with_state(store);

    let port = std::env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let addr = format!("0.0.0.0:{}", port);
    println!("Listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
