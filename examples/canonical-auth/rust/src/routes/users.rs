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

pub async fn list_users(
    auth_ctx: AuthContext,
    State(store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if !auth_ctx.has_permission("iam:user:read") {
        return StatusCode::FORBIDDEN.into_response();
    }
    let tenant_id = match auth_ctx.tenant_id {
        Some(ref id) => id,
        None => return StatusCode::FORBIDDEN.into_response(),
    };

    let tenant_users: Vec<_> = store.users.iter()
        .filter(|u| store.verify_membership(&u.id, tenant_id))
        .collect();

    (StatusCode::OK, Json(tenant_users)).into_response()
}

pub async fn invite_user(
    auth_ctx: AuthContext,
    State(_store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if !auth_ctx.has_permission("iam:user:invite") {
        return StatusCode::FORBIDDEN.into_response();
    }
    if auth_ctx.tenant_id.is_none() {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::CREATED, Json(json!({"message": "User invited"}))).into_response()
}

pub async fn get_user(
    auth_ctx: AuthContext,
    Path(id): Path<String>,
    State(store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if !auth_ctx.has_permission("iam:user:read") {
        return StatusCode::FORBIDDEN.into_response();
    }
    let tenant_id = match auth_ctx.tenant_id {
        Some(ref tid) => tid,
        None => return StatusCode::FORBIDDEN.into_response(),
    };

    let user = match store.get_user_by_id(&id) {
        Some(u) => u,
        None => return StatusCode::NOT_FOUND.into_response(),
    };

    if !store.verify_membership(&user.id, tenant_id) {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::OK, Json(user)).into_response()
}

pub async fn update_user(
    auth_ctx: AuthContext,
    Path(id): Path<String>,
    State(store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    if !auth_ctx.has_permission("iam:user:update") {
        return StatusCode::FORBIDDEN.into_response();
    }
    let tenant_id = match auth_ctx.tenant_id {
        Some(ref tid) => tid,
        None => return StatusCode::FORBIDDEN.into_response(),
    };

    let user = match store.get_user_by_id(&id) {
        Some(u) => u,
        None => return StatusCode::NOT_FOUND.into_response(),
    };

    if !store.verify_membership(&user.id, tenant_id) {
        return StatusCode::FORBIDDEN.into_response();
    }

    (StatusCode::OK, Json(json!({"message": "User updated"}))).into_response()
}
