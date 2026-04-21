use std::sync::Arc;
use axum::{
    extract::State,
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde_json::json;

use crate::auth::claims::AuthContext;
use crate::domain::store::InMemoryStore;

pub async fn list_tenants(
    auth_ctx: AuthContext,
    State(_store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if auth_ctx.tenant_role != "super_admin" {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::OK, Json(json!([]))).into_response()
}

pub async fn create_tenant(
    auth_ctx: AuthContext,
    State(_store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if auth_ctx.tenant_role != "super_admin" {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::CREATED, Json(json!({"message": "Tenant created"}))).into_response()
}
