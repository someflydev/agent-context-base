use std::sync::Arc;
use axum::{
    extract::{Extension, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use jsonwebtoken::EncodingKey;
use serde_json::json;

use crate::auth::token::issue_token;
use crate::domain::store::InMemoryStore;

#[derive(serde::Deserialize)]
pub struct AuthRequest {
    pub email: String,
    pub password: Option<String>,
}

pub async fn token_handler(
    State(store): State<Arc<InMemoryStore>>,
    Extension(encoding_key): Extension<EncodingKey>,
    Json(payload): Json<AuthRequest>,
) -> impl IntoResponse {
    let user = match store.get_user_by_email(&payload.email) {
        Some(u) => u,
        None => return (StatusCode::UNAUTHORIZED, Json(json!({"error": "invalid credentials"}))).into_response(),
    };

    if payload.password.as_deref() != Some("password123") {
        return (StatusCode::UNAUTHORIZED, Json(json!({"error": "invalid credentials"}))).into_response();
    }

    match issue_token(user, &store, &encoding_key) {
        Ok(token) => (StatusCode::OK, Json(json!({"access_token": token}))).into_response(),
        Err(_) => (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"error": "could not issue token"}))).into_response(),
    }
}
