use std::collections::HashSet;
use std::env;
use std::sync::Arc;

use axum::{
    async_trait,
    extract::FromRequestParts,
    http::{request::Parts, StatusCode},
};
use jsonwebtoken::{decode, DecodingKey, Validation, Algorithm};
use chrono::TimeZone;

use super::claims::{AuthContext, Claims};
use crate::domain::store::InMemoryStore;

#[async_trait]
impl<S> FromRequestParts<S> for AuthContext
where
    S: Send + Sync,
    Arc<InMemoryStore>: axum::extract::FromRef<S>,
{
    type Rejection = StatusCode;

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let auth_header = parts.headers.get("Authorization")
            .and_then(|val| val.to_str().ok())
            .ok_or(StatusCode::UNAUTHORIZED)?;

        if !auth_header.starts_with("Bearer ") {
            return Err(StatusCode::UNAUTHORIZED);
        }
        let token = &auth_header[7..];

        let (decoding_key, alg) = if let Ok(secret) = env::var("TENANTCORE_TEST_SECRET") {
            if !secret.is_empty() {
                (DecodingKey::from_secret(secret.as_bytes()), Algorithm::HS256)
            } else {
                return Err(StatusCode::UNAUTHORIZED);
            }
        } else {
            // Note: In real app, we'd load the public key from state or config
            // For canonical example parity with Go, if no secret, we'd need RSA public key.
            // Since extractors don't easily get the key unless passed via state, we can use an Extension
            // But we will fetch the key from the Extension
            let key = parts.extensions.get::<DecodingKey>().ok_or(StatusCode::INTERNAL_SERVER_ERROR)?;
            (key.clone(), Algorithm::RS256)
        };

        let mut validation = Validation::new(alg);
        validation.validate_exp = true;
        validation.validate_nbf = true;
        validation.aud = Some(HashSet::from(["tenantcore-api".to_string()]));
        validation.iss = Some(HashSet::from(["tenantcore-auth".to_string()]));
        validation.required_spec_claims = HashSet::from([
            "iss".into(), "aud".into(), "sub".into(), "exp".into(),
            "iat".into(), "nbf".into(), "jti".into(),
        ]);

        let token_data = decode::<Claims>(token, &decoding_key, &validation)
            .map_err(|_| StatusCode::UNAUTHORIZED)?;

        let claims = token_data.claims;

        let store = axum::extract::State::<Arc<InMemoryStore>>::from_request_parts(parts, state)
            .await
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
            .0;

        let user = store.get_user_by_id(&claims.sub).ok_or(StatusCode::UNAUTHORIZED)?;

        if claims.acl_ver != user.acl_ver {
            return Err(StatusCode::UNAUTHORIZED);
        }

        if let Some(ref tenant_id) = claims.tenant_id {
            if !store.verify_membership(&user.id, tenant_id) {
                return Err(StatusCode::FORBIDDEN);
            }
        }

        Ok(AuthContext {
            sub: claims.sub,
            email: user.email.clone(),
            tenant_id: claims.tenant_id,
            tenant_role: claims.tenant_role,
            groups: claims.groups,
            permissions: claims.permissions,
            acl_ver: claims.acl_ver,
            issued_at: chrono::Utc.timestamp_opt(claims.iat as i64, 0).unwrap(),
            expires_at: chrono::Utc.timestamp_opt(claims.exp as i64, 0).unwrap(),
        })
    }
}
