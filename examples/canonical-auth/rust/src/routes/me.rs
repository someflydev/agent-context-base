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
use crate::registry::routes::get_allowed_routes;

pub async fn me_handler(
    auth_ctx: AuthContext,
    State(store): State<Arc<InMemoryStore>>,
) -> impl IntoResponse {
    let user = match store.get_user_by_id(&auth_ctx.sub) {
        Some(u) => u,
        None => return StatusCode::UNAUTHORIZED.into_response(),
    };

    let tenant_name = auth_ctx.tenant_id.as_ref()
        .and_then(|id| store.get_tenant_name(id))
        .unwrap_or("");

    let is_super_admin = auth_ctx.tenant_role == "super_admin";
    let allowed_routes = get_allowed_routes(&auth_ctx.permissions, is_super_admin);

    let guide_sections = if is_super_admin {
        vec![]
    } else {
        vec!["User Management", "Billing"]
    };

    let body = json!({
        "sub": auth_ctx.sub,
        "email": auth_ctx.email,
        "display_name": user.display_name,
        "tenant_id": auth_ctx.tenant_id,
        "tenant_name": tenant_name,
        "tenant_role": auth_ctx.tenant_role,
        "groups": auth_ctx.groups,
        "permissions": auth_ctx.permissions,
        "acl_ver": auth_ctx.acl_ver,
        "allowed_routes": allowed_routes,
        "guide_sections": guide_sections,
        "issued_at": auth_ctx.issued_at,
        "expires_at": auth_ctx.expires_at,
    });

    (StatusCode::OK, Json(body)).into_response()
}
