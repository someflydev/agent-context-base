pub mod auth;
pub mod domain;
pub mod registry;
pub mod routes;

use std::sync::Arc;
use std::path::Path;

use axum::{
    routing::{get, post, patch},
    Router,
    extract::Extension,
};
use jsonwebtoken::{EncodingKey, DecodingKey};
use domain::store::InMemoryStore;

pub fn create_app(store: Arc<InMemoryStore>, encoding_key: EncodingKey, decoding_key: DecodingKey) -> Router {
    Router::new()
        .route("/health", get(routes::health::health_handler))
        .route("/auth/token", post(routes::auth::token_handler))
        .route("/me", get(routes::me::me_handler))
        .route("/users", get(routes::users::list_users).post(routes::users::invite_user))
        .route("/users/:id", get(routes::users::get_user).patch(routes::users::update_user))
        .route("/groups", get(routes::groups::list_groups).post(routes::groups::create_group))
        .route("/groups/:id/permissions", post(routes::groups::assign_permission))
        .route("/groups/:id/users", post(routes::groups::assign_user))
        .route("/admin/tenants", get(routes::admin::list_tenants).post(routes::admin::create_tenant))
        .layer(Extension(encoding_key))
        .layer(Extension(decoding_key))
        .with_state(store)
}
