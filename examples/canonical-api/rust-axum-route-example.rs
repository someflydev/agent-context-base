use axum::{
    extract::{Path, Query, State},
    response::IntoResponse,
    routing::get,
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub report_service: Arc<ReportService>,
}

#[derive(Deserialize)]
pub struct ListReportsQuery {
    pub limit: Option<usize>,
}

#[derive(Serialize)]
pub struct ReportSummary {
    pub report_id: String,
    pub total_events: i64,
}

pub fn router(state: AppState) -> Router {
    Router::new()
        .route("/tenants/:tenant_id/reports", get(list_reports))
        .with_state(state)
}

async fn list_reports(
    State(state): State<AppState>,
    Path(tenant_id): Path<String>,
    Query(query): Query<ListReportsQuery>,
) -> impl IntoResponse {
    let limit = query.limit.unwrap_or(20).min(100);
    let reports = state
        .report_service
        .list_recent(tenant_id, limit)
        .await
        .expect("surface a real error type in the app");

    Json(reports)
}

pub struct ReportService;

impl ReportService {
    pub async fn list_recent(
        &self,
        _tenant_id: String,
        _limit: usize,
    ) -> Result<Vec<ReportSummary>, anyhow::Error> {
        Ok(vec![ReportSummary {
            report_id: "daily-traffic".to_string(),
            total_events: 420,
        }])
    }
}

