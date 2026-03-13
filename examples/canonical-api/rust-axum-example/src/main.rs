use axum::{routing::get, Json, Router};
use std::net::SocketAddr;

async fn healthz() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "ok",
        "service": "rust-axum-example"
    }))
}

async fn report_summary() -> Json<serde_json::Value> {
    Json(serde_json::json!([
        {
            "report_id": "daily-signups",
            "tenant_id": "acme",
            "total_events": 42
        }
    ]))
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/healthz", get(healthz))
        .route("/reports/summary", get(report_summary));

    let address = SocketAddr::from(([0, 0, 0, 0], 3000));
    let listener = tokio::net::TcpListener::bind(address)
        .await
        .expect("failed to bind listener");
    axum::serve(listener, app).await.expect("server error");
}
