use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: String,
    pub email: String,
    pub display_name: String,
    pub tenant_id: Option<String>,
    pub created_at: DateTime<Utc>,
    pub is_active: bool,
    pub acl_ver: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tenant {
    pub id: String,
    pub slug: String,
    pub name: String,
    pub created_at: DateTime<Utc>,
    pub is_active: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Membership {
    pub id: String,
    pub user_id: String,
    pub tenant_id: Option<String>,
    pub tenant_role: String,
    pub created_at: DateTime<Utc>,
    pub is_active: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Group {
    pub id: String,
    pub tenant_id: String,
    pub slug: String,
    pub name: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Permission {
    pub id: String,
    pub name: String,
    pub description: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GroupPermission {
    pub id: String,
    pub group_id: String,
    pub permission_id: String,
    pub granted_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserGroup {
    pub id: String,
    pub user_id: String,
    pub group_id: String,
    pub joined_at: DateTime<Utc>,
}
