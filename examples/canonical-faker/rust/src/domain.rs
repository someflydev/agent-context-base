use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub struct Organization {
    pub id: String,
    pub name: String,
    pub slug: String,
    pub plan: String,
    pub region: String,
    pub created_at: DateTime<Utc>,
    pub owner_email: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub struct User {
    pub id: String,
    pub email: String,
    pub full_name: String,
    pub locale: String,
    pub timezone: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub struct Membership {
    pub id: String,
    pub org_id: String,
    pub user_id: String,
    pub role: String,
    pub joined_at: DateTime<Utc>,
    pub invited_by: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub struct Project {
    pub id: String,
    pub org_id: String,
    pub name: String,
    pub status: String,
    pub created_by: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub struct AuditEvent {
    pub id: String,
    pub org_id: String,
    pub user_id: String,
    pub project_id: String,
    pub action: String,
    pub resource_type: String,
    pub resource_id: String,
    pub ts: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub struct ApiKey {
    pub id: String,
    pub org_id: String,
    pub created_by: String,
    pub name: String,
    pub key_prefix: String,
    pub created_at: DateTime<Utc>,
    pub last_used_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub struct Invitation {
    pub id: String,
    pub org_id: String,
    pub invited_email: String,
    pub role: String,
    pub invited_by: String,
    pub expires_at: DateTime<Utc>,
    pub accepted_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Dataset {
    pub profile_name: String,
    pub seed: u64,
    pub organizations: Vec<Organization>,
    pub users: Vec<User>,
    pub memberships: Vec<Membership>,
    pub projects: Vec<Project>,
    pub audit_events: Vec<AuditEvent>,
    pub api_keys: Vec<ApiKey>,
    pub invitations: Vec<Invitation>,
}
