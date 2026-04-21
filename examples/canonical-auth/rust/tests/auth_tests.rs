mod common;

use std::time::{SystemTime, UNIX_EPOCH};
use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use serde_json::{json, Value};
use tower::ServiceExt;
use jsonwebtoken::{encode, EncodingKey, Header, Algorithm};
use canonical_auth_rust::auth::claims::Claims;
use canonical_auth_rust::auth::token::issue_token;

fn issue_test_token(store: &canonical_auth_rust::domain::store::InMemoryStore, secret: &[u8], email: &str) -> String {
    let user = store.get_user_by_email(email).unwrap();
    let encoding_key = EncodingKey::from_secret(secret);
    issue_token(user, store, &encoding_key).unwrap()
}

#[tokio::test]
async fn test_token_issue_success() {
    let (app, _store, _) = common::setup_test_app();
    
    let req = Request::builder()
        .method("POST")
        .uri("/auth/token")
        .header("Content-Type", "application/json")
        .body(Body::from(json!({"email": "admin@acme.example", "password": "password123"}).to_string()))
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_token_invalid_credentials() {
    let (app, _store, _) = common::setup_test_app();
    
    let req = Request::builder()
        .method("POST")
        .uri("/auth/token")
        .header("Content-Type", "application/json")
        .body(Body::from(json!({"email": "admin@acme.example", "password": "wrong"}).to_string()))
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn test_token_expired_rejection() {
    let (app, store, secret) = common::setup_test_app();
    let user = store.get_user_by_email("admin@acme.example").unwrap();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs() as usize;
    let exp = now - 900; // in the past

    let claims = Claims {
        iss: "tenantcore-auth".into(),
        aud: vec!["tenantcore-api".into()],
        sub: user.id.clone(),
        exp,
        iat: exp - 900,
        nbf: exp - 900,
        jti: "test".into(),
        tenant_id: None,
        tenant_role: "tenant_admin".into(),
        groups: vec![],
        permissions: vec![],
        acl_ver: user.acl_ver,
    };
    
    let token = encode(&Header::new(Algorithm::HS256), &claims, &EncodingKey::from_secret(&secret)).unwrap();

    let req = Request::builder()
        .method("GET")
        .uri("/me")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn test_token_stale_acl_ver() {
    let (app, store, secret) = common::setup_test_app();
    let user = store.get_user_by_email("admin@acme.example").unwrap();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs() as usize;
    
    let claims = Claims {
        iss: "tenantcore-auth".into(),
        aud: vec!["tenantcore-api".into()],
        sub: user.id.clone(),
        exp: now + 900,
        iat: now,
        nbf: now,
        jti: "test".into(),
        tenant_id: None,
        tenant_role: "tenant_admin".into(),
        groups: vec![],
        permissions: vec![],
        acl_ver: user.acl_ver - 1, // Stale
    };
    
    let token = encode(&Header::new(Algorithm::HS256), &claims, &EncodingKey::from_secret(&secret)).unwrap();

    let req = Request::builder()
        .method("GET")
        .uri("/me")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn test_get_me_success() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "admin@acme.example");

    let req = Request::builder()
        .method("GET")
        .uri("/me")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_get_me_unauthorized() {
    let (app, _, _) = common::setup_test_app();
    let req = Request::builder()
        .method("GET")
        .uri("/me")
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn test_rbac_permission_granted() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "alice@acme.example"); // has iam:user:read

    let req = Request::builder()
        .method("GET")
        .uri("/users")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_rbac_permission_denied() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "bob@acme.example"); // has no iam:user:invite

    let req = Request::builder()
        .method("POST")
        .uri("/users")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::FORBIDDEN);
}

#[tokio::test]
async fn test_cross_tenant_denial() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "alice@acme.example");
    let carol = store.get_user_by_email("carol@globex.example").unwrap();

    let req = Request::builder()
        .method("GET")
        .uri(format!("/users/{}", carol.id))
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::FORBIDDEN);
}

#[tokio::test]
async fn test_super_admin_access() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "superadmin@tenantcore.dev");

    let req = Request::builder()
        .method("GET")
        .uri("/admin/tenants")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_super_admin_tenant_scoped_denial() {
    let (app, store, secret) = common::setup_test_app();
    let token = issue_test_token(&store, &secret, "superadmin@tenantcore.dev");

    let req = Request::builder()
        .method("GET")
        .uri("/users")
        .header("Authorization", format!("Bearer {}", token))
        .body(Body::empty())
        .unwrap();

    let response = app.oneshot(req).await.unwrap();
    assert_eq!(response.status(), StatusCode::FORBIDDEN);
}

#[tokio::test]
async fn test_me_allowed_routes_match_permissions() {
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
}
