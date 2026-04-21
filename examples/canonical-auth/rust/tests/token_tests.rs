mod common;

use std::time::{SystemTime, UNIX_EPOCH};
use jsonwebtoken::{decode, DecodingKey, Validation, Algorithm};

use canonical_auth_rust::auth::claims::Claims;
use canonical_auth_rust::auth::token::issue_token;
use jsonwebtoken::EncodingKey;

#[tokio::test]
async fn test_issue_token_claim_shape() {
    let (_, store, secret) = common::setup_test_app();
    let user = store.get_user_by_email("alice@acme.example").unwrap();
    let encoding_key = EncodingKey::from_secret(&secret);

    let token_string = issue_token(user, &store, &encoding_key).unwrap();

    let mut validation = Validation::new(Algorithm::HS256);
    validation.insecure_disable_signature_validation(); // just checking shape
    validation.set_audience(&["tenantcore-api"]);

    let decoding_key = DecodingKey::from_secret(&secret);
    let token_data = decode::<Claims>(&token_string, &decoding_key, &validation).unwrap();
    let claims = token_data.claims;

    assert_eq!(claims.sub, user.id);
    assert!(claims.tenant_id.is_some());
    assert_eq!(claims.tenant_role, "tenant_member");
    assert!(!claims.groups.is_empty());
    assert_eq!(claims.acl_ver, user.acl_ver);
}

#[tokio::test]
async fn test_issue_token_expiry_15_min() {
    let (_, store, secret) = common::setup_test_app();
    let user = store.get_user_by_email("alice@acme.example").unwrap();
    let encoding_key = EncodingKey::from_secret(&secret);

    let token_string = issue_token(user, &store, &encoding_key).unwrap();
    let decoding_key = DecodingKey::from_secret(&secret);
    
    let mut validation = Validation::new(Algorithm::HS256);
    validation.set_audience(&["tenantcore-api"]);
    let token_data = decode::<Claims>(&token_string, &decoding_key, &validation).unwrap();
    let claims = token_data.claims;

    let diff = claims.exp - claims.iat;
    assert_eq!(diff, 900); // 15 mins
}

#[tokio::test]
async fn test_issue_token_permissions_match_store() {
    let (_, store, secret) = common::setup_test_app();
    let user = store.get_user_by_email("alice@acme.example").unwrap();
    let encoding_key = EncodingKey::from_secret(&secret);

    let token_string = issue_token(user, &store, &encoding_key).unwrap();
    let decoding_key = DecodingKey::from_secret(&secret);
    
    let mut validation = Validation::new(Algorithm::HS256);
    validation.set_audience(&["tenantcore-api"]);
    let token_data = decode::<Claims>(&token_string, &decoding_key, &validation).unwrap();
    let claims = token_data.claims;

    let effective_perms = store.get_effective_permissions(&user.id);
    assert_eq!(claims.permissions.len(), effective_perms.len());
}
