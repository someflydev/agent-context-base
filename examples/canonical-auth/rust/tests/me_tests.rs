mod common;

use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use tower::ServiceExt;
use canonical_auth_rust::auth::token::issue_token;
use jsonwebtoken::EncodingKey;
use http_body_util::BodyExt;
use serde_json::Value;

fn issue_test_token(store: &canonical_auth_rust::domain::store::InMemoryStore, secret: &[u8], email: &str) -> String {
    let user = store.get_user_by_email(email).unwrap();
    let encoding_key = EncodingKey::from_secret(secret);
    issue_token(user, store, &encoding_key).unwrap()
}

#[tokio::test]
async fn test_me_response_fields() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "alice@acme.example");

    let req = Request::builder()
        .method("GET")
        .uri("/me")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::OK);

    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    let resp: Value = serde_json::from_slice(&bytes).unwrap();

    assert!(resp.get("sub").is_some());
    assert!(resp.get("email").is_some());
    assert!(resp.get("display_name").is_some());
    assert!(resp.get("tenant_id").is_some());
    assert!(resp.get("tenant_role").is_some());
    assert!(resp.get("groups").is_some());
    assert!(resp.get("permissions").is_some());
    assert!(resp.get("acl_ver").is_some());
    assert!(resp.get("allowed_routes").is_some());
    assert!(resp.get("guide_sections").is_some());
    assert!(resp.get("issued_at").is_some());
    assert!(resp.get("expires_at").is_some());
}

#[tokio::test]
async fn test_me_allowed_routes_filtered() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "bob@acme.example");

    let req = Request::builder()
        .method("GET")
        .uri("/me")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    let resp: Value = serde_json::from_slice(&bytes).unwrap();

    let allowed_routes = resp["allowed_routes"].as_array().unwrap();
    let mut has_user_read = false;
    let mut has_user_invite = false;

    for r in allowed_routes {
        let perm = r["permission"].as_str().unwrap();
        if perm == "iam:user:read" {
            has_user_read = true;
        }
        if perm == "iam:user:invite" {
            has_user_invite = true;
        }
    }

    assert!(has_user_read);
    assert!(!has_user_invite);
}

#[tokio::test]
async fn test_me_super_admin_shape() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "superadmin@tenantcore.dev");

    let req = Request::builder()
        .method("GET")
        .uri("/me")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    let bytes = response.into_body().collect().await.unwrap().to_bytes();
    let resp: Value = serde_json::from_slice(&bytes).unwrap();

    assert!(resp["tenant_id"].is_null());
    assert_eq!(resp["tenant_role"].as_str().unwrap(), "super_admin");
    assert_eq!(resp["groups"].as_array().unwrap().len(), 0);

    let allowed_routes = resp["allowed_routes"].as_array().unwrap();
    let mut has_admin_route = false;
    let mut has_tenant_scoped = false;

    for r in allowed_routes {
        if r["super_admin_only"].as_bool().unwrap_or(false) {
            has_admin_route = true;
        }
        if r["tenant_scoped"].as_bool().unwrap_or(false) {
            has_tenant_scoped = true;
        }
    }

    assert!(has_admin_route);
    assert!(!has_tenant_scoped);
}
