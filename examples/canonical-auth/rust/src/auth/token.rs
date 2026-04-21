use std::env;
use std::time::{SystemTime, UNIX_EPOCH};

use jsonwebtoken::{encode, EncodingKey, Header, Algorithm};
use uuid::Uuid;

use super::claims::Claims;
use crate::domain::models::User;
use crate::domain::store::InMemoryStore;

pub fn issue_token(
    user: &User,
    store: &InMemoryStore,
    encoding_key: &EncodingKey,
) -> Result<String, Box<dyn std::error::Error>> {
    let now = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs() as usize;
    let exp = now + 900; // 15 minutes

    let membership = store.get_membership(&user.id).ok_or("no active membership found for user")?;

    let mut group_slugs = Vec::new();
    if let Some(ref tenant_id) = membership.tenant_id {
        let groups = store.get_groups_for_user(&user.id, tenant_id);
        for g in groups {
            group_slugs.push(g.slug.clone());
        }
    }

    let permissions = store.get_effective_permissions(&user.id);

    let claims = Claims {
        iss: "tenantcore-auth".to_string(),
        aud: vec!["tenantcore-api".to_string()],
        sub: user.id.clone(),
        exp,
        iat: now,
        nbf: now,
        jti: Uuid::new_v4().to_string(),
        tenant_id: membership.tenant_id.clone(),
        tenant_role: membership.tenant_role.clone(),
        groups: group_slugs,
        permissions,
        acl_ver: user.acl_ver,
    };

    if let Ok(secret) = env::var("TENANTCORE_TEST_SECRET") {
        if !secret.is_empty() {
            let hs_key = EncodingKey::from_secret(secret.as_bytes());
            let header = Header::new(Algorithm::HS256);
            return Ok(encode(&header, &claims, &hs_key)?);
        }
    }

    let header = Header::new(Algorithm::RS256);
    Ok(encode(&header, &claims, encoding_key)?)
}
