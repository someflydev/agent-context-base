use std::collections::{HashMap, HashSet};

use chrono::Duration;
use serde::Serialize;

use crate::domain::{Dataset, Membership};
use crate::pools::{base_time, build_graph};

#[derive(Debug, Clone, Serialize)]
pub struct ValidationReport {
    pub ok: bool,
    pub violations: Vec<String>,
    pub counts: HashMap<String, usize>,
    pub seed: u64,
    pub profile_name: String,
}

pub fn validate(dataset: &Dataset) -> ValidationReport {
    let mut violations = Vec::new();
    let counts = HashMap::from([
        ("organizations".to_string(), dataset.organizations.len()),
        ("users".to_string(), dataset.users.len()),
        ("memberships".to_string(), dataset.memberships.len()),
        ("projects".to_string(), dataset.projects.len()),
        ("audit_events".to_string(), dataset.audit_events.len()),
        ("api_keys".to_string(), dataset.api_keys.len()),
        ("invitations".to_string(), dataset.invitations.len()),
    ]);
    let graph = build_graph(dataset);

    let orgs: HashMap<_, _> = dataset
        .organizations
        .iter()
        .map(|org| (org.id.clone(), org))
        .collect();
    let users: HashMap<_, _> = dataset.users.iter().map(|user| (user.id.clone(), user)).collect();
    let projects: HashMap<_, _> = dataset
        .projects
        .iter()
        .map(|project| (project.id.clone(), project))
        .collect();

    let mut org_ids = HashSet::new();
    for org in &dataset.organizations {
        if !org_ids.insert(org.id.clone()) {
            violations.push(format!("duplicate organizations.id: {}", org.id));
        }
    }

    let mut user_emails = HashSet::new();
    for user in &dataset.users {
        if !user_emails.insert(user.email.to_lowercase()) {
            violations.push(format!("duplicate users.email: {}", user.email));
        }
    }

    let mut membership_ids = HashSet::new();
    for membership in &dataset.memberships {
        membership_ids.insert(membership.id.clone());
        let Some(org) = orgs.get(&membership.org_id) else {
            violations.push(format!("membership missing org: {}", membership.id));
            continue;
        };
        if !users.contains_key(&membership.user_id) {
            violations.push(format!("membership missing user: {}", membership.id));
            continue;
        }
        if membership.joined_at < org.created_at {
            violations.push(format!("Rule A violated by membership {}", membership.id));
        }
        if let Some(invited_by) = &membership.invited_by {
            if !users.contains_key(invited_by) {
                violations.push(format!("membership invited_by missing user: {}", membership.id));
            }
        }
    }

    let mut api_key_ids = HashSet::new();
    let mut key_prefixes = HashSet::new();
    for api_key in &dataset.api_keys {
        api_key_ids.insert(api_key.id.clone());
        if !graph
            .org_member_map
            .get(&api_key.org_id)
            .is_some_and(|members| members.contains(&api_key.created_by))
        {
            violations.push(format!("Rule G violated by api_key {}", api_key.id));
        }
        if !key_prefixes.insert(api_key.key_prefix.clone()) {
            violations.push(format!("duplicate api_key.key_prefix: {}", api_key.key_prefix));
        }
        if let Some(last_used) = api_key.last_used_at {
            if last_used < api_key.created_at {
                violations.push(format!("api_key last_used_at before created_at: {}", api_key.id));
            }
        }
    }

    let mut invitation_ids = HashSet::new();
    for invitation in &dataset.invitations {
        invitation_ids.insert(invitation.id.clone());
        if !graph
            .org_member_map
            .get(&invitation.org_id)
            .is_some_and(|members| members.contains(&invitation.invited_by))
        {
            violations.push(format!("Rule H violated by invitation {}", invitation.id));
        }
        if graph
            .org_member_map
            .get(&invitation.org_id)
            .into_iter()
            .flatten()
            .filter_map(|member_id| graph.user_email_by_id.get(member_id))
            .any(|email| email == &invitation.invited_email.to_lowercase())
        {
            violations.push(format!("Rule I violated by invitation {}", invitation.id));
        }
        if invitation.expires_at <= base_time() {
            violations.push(format!("invitation expiry must be in the future: {}", invitation.id));
        }
        if invitation.expires_at > base_time() + Duration::days(30) {
            violations.push(format!("invitation expiry must be within 30 days: {}", invitation.id));
        }
        if invitation
            .accepted_at
            .is_some_and(|accepted_at| accepted_at > base_time())
        {
            violations.push(format!("invitation accepted_at must be in the past: {}", invitation.id));
        }
    }

    for project in &dataset.projects {
        let Some(org) = orgs.get(&project.org_id) else {
            violations.push(format!("project missing org: {}", project.id));
            continue;
        };
        if project.created_at < org.created_at {
            violations.push(format!("Rule B violated by project {}", project.id));
        }
        if !graph
            .org_member_map
            .get(&project.org_id)
            .is_some_and(|members| members.contains(&project.created_by))
        {
            violations.push(format!("Rule C violated by project {}", project.id));
        }
    }

    for event in &dataset.audit_events {
        let Some(project) = projects.get(&event.project_id) else {
            violations.push(format!("audit_event missing project: {}", event.id));
            continue;
        };
        if !orgs.contains_key(&event.org_id) {
            violations.push(format!("audit_event missing org: {}", event.id));
            continue;
        }
        if !graph
            .org_member_map
            .get(&event.org_id)
            .is_some_and(|members| members.contains(&event.user_id))
        {
            violations.push(format!("Rule D violated by audit_event {}", event.id));
        }
        if project.org_id != event.org_id {
            violations.push(format!("Rule E violated by audit_event {}", event.id));
        }
        if event.ts < project.created_at {
            violations.push(format!("Rule F violated by audit_event {}", event.id));
        }
        if let Some(membership) = graph
            .membership_by_org_user
            .get(&format!("{}:{}", event.org_id, event.user_id))
        {
            if event.ts < membership.joined_at {
                violations.push(format!("audit event before membership joined_at: {}", event.id));
            }
        }
        match event.resource_type.as_str() {
            "project" if !projects.contains_key(&event.resource_id) => {
                violations.push(format!("audit event resource project missing: {}", event.id));
            }
            "user" if !users.contains_key(&event.resource_id) => {
                violations.push(format!("audit event resource user missing: {}", event.id));
            }
            "membership" if !membership_ids.contains(&event.resource_id) => {
                violations.push(format!("audit event resource membership missing: {}", event.id));
            }
            "api_key" if !api_key_ids.contains(&event.resource_id) => {
                violations.push(format!("audit event resource api_key missing: {}", event.id));
            }
            "invitation" if !invitation_ids.contains(&event.resource_id) => {
                violations.push(format!("audit event resource invitation missing: {}", event.id));
            }
            _ => {}
        }
    }

    ValidationReport {
        ok: violations.is_empty(),
        violations,
        counts,
        seed: dataset.seed,
        profile_name: dataset.profile_name.clone(),
    }
}

#[allow(dead_code)]
fn membership_is_zero(membership: &Membership) -> bool {
    membership.id.is_empty()
}
