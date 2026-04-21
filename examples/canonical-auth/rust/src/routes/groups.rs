use std::sync::Arc;
use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde_json::json;

use crate::auth::claims::AuthContext;
use crate::domain::store::InMemoryStore;

pub async fn list_groups(
    auth_ctx: AuthContext,
    State(_store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if !auth_ctx.has_permission("iam:group:read") {
        return StatusCode::FORBIDDEN.into_response();
    }
    if auth_ctx.tenant_id.is_none() {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::OK, Json(json!([]))).into_response()
}

pub async fn create_group(
    auth_ctx: AuthContext,
    State(_store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if !auth_ctx.has_permission("iam:group:create") {
        return StatusCode::FORBIDDEN.into_response();
    }
    if auth_ctx.tenant_id.is_none() {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::CREATED, Json(json!({"message": "Group created"}))).into_response()
}

pub async fn assign_permission(
    auth_ctx: AuthContext,
    Path(_id): Path<String>,
    State(_store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if !auth_ctx.has_permission("iam:group:assign_permission") {
        return StatusCode::FORBIDDEN.into_response();
    }
    if auth_ctx.tenant_id.is_none() {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::OK, Json(json!({"message": "Permission assigned"}))).into_response()
}

pub async fn assign_user(
    auth_ctx: AuthContext,
    Path(_id): Path<String>,
    State(_store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if !auth_ctx.has_permission("iam:group:assign_user") {
        return StatusCode::FORBIDDEN.into_response();
    }
    if auth_ctx.tenant_id.is_none() {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::OK, Json(json!({"message": "User assigned"}))).into_response()
}
