use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::Path;

use super::models::*;

#[derive(Debug, Clone)]
pub struct InMemoryStore {
    pub users: Vec<User>,
    pub tenants: Vec<Tenant>,
    pub memberships: Vec<Membership>,
    pub groups: Vec<Group>,
    pub permissions: Vec<Permission>,
    pub group_permissions: Vec<GroupPermission>,
    pub user_groups: Vec<UserGroup>,
}

impl InMemoryStore {
    pub fn load_from_fixtures(fixture_dir: &Path) -> Result<Self, Box<dyn std::error::Error>> {
        let users: Vec<User> = serde_json::from_slice(&fs::read(fixture_dir.join("users.json"))?)?;
        let tenants: Vec<Tenant> = serde_json::from_slice(&fs::read(fixture_dir.join("tenants.json"))?)?;
        let memberships: Vec<Membership> = serde_json::from_slice(&fs::read(fixture_dir.join("memberships.json"))?)?;
        let groups: Vec<Group> = serde_json::from_slice(&fs::read(fixture_dir.join("groups.json"))?)?;
        let permissions: Vec<Permission> = serde_json::from_slice(&fs::read(fixture_dir.join("permissions.json"))?)?;
        let group_permissions: Vec<GroupPermission> = serde_json::from_slice(&fs::read(fixture_dir.join("group_permissions.json"))?)?;
        let user_groups: Vec<UserGroup> = serde_json::from_slice(&fs::read(fixture_dir.join("user_groups.json"))?)?;

        Ok(Self {
            users,
            tenants,
            memberships,
            groups,
            permissions,
            group_permissions,
            user_groups,
        })
    }

    pub fn get_user_by_id(&self, id: &str) -> Option<&User> {
        self.users.iter().find(|u| u.id == id)
    }

    pub fn get_user_by_email(&self, email: &str) -> Option<&User> {
        self.users.iter().find(|u| u.email == email)
    }

    pub fn get_tenant_by_id(&self, id: &str) -> Option<&Tenant> {
        self.tenants.iter().find(|t| t.id == id)
    }

    pub fn get_tenant_name(&self, tenant_id: &str) -> Option<&str> {
        self.get_tenant_by_id(tenant_id).map(|t| t.name.as_str())
    }

    pub fn get_membership(&self, user_id: &str) -> Option<&Membership> {
        self.memberships.iter().find(|m| m.user_id == user_id && m.is_active)
    }

    pub fn verify_membership(&self, user_id: &str, tenant_id: &str) -> bool {
        self.memberships.iter().any(|m| {
            m.user_id == user_id && m.is_active && m.tenant_id.as_deref() == Some(tenant_id)
        })
    }

    pub fn get_groups_for_user(&self, user_id: &str, tenant_id: &str) -> Vec<&Group> {
        let user_group_ids: HashSet<_> = self.user_groups.iter()
            .filter(|ug| ug.user_id == user_id)
            .map(|ug| &ug.group_id)
            .collect();

        self.groups.iter()
            .filter(|g| g.tenant_id == tenant_id && user_group_ids.contains(&g.id))
            .collect()
    }

    pub fn get_effective_permissions(&self, user_id: &str) -> Vec<String> {
        let user_group_ids: HashSet<_> = self.user_groups.iter()
            .filter(|ug| ug.user_id == user_id)
            .map(|ug| &ug.group_id)
            .collect();

        let group_ids: HashSet<_> = self.groups.iter()
            .filter(|g| user_group_ids.contains(&g.id))
            .map(|g| &g.id)
            .collect();

        let perm_ids: HashSet<_> = self.group_permissions.iter()
            .filter(|gp| group_ids.contains(&gp.group_id))
            .map(|gp| &gp.permission_id)
            .collect();

        let mut perms: Vec<String> = self.permissions.iter()
            .filter(|p| perm_ids.contains(&p.id))
            .map(|p| p.name.clone())
            .collect();
        perms.sort();
        perms
    }
}
