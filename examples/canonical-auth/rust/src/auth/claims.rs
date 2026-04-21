use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Claims {
    pub iss: String,
    pub aud: Vec<String>,
    pub sub: String,
    pub exp: usize,
    pub iat: usize,
    pub nbf: usize,
    pub jti: String,
    pub tenant_id: Option<String>,
    pub tenant_role: String,
    pub groups: Vec<String>,
    pub permissions: Vec<String>,
    pub acl_ver: i32,
}

#[derive(Debug, Clone)]
pub struct AuthContext {
    pub sub: String,
    pub email: String,
    pub tenant_id: Option<String>,
    pub tenant_role: String,
    pub groups: Vec<String>,
    pub permissions: Vec<String>,
    pub acl_ver: i32,
    pub issued_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
}

impl AuthContext {
    pub fn has_permission(&self, permission: &str) -> bool {
        self.permissions.iter().any(|p| p == permission)
    }
}
