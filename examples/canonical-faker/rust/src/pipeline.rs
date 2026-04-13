use std::collections::{HashMap, HashSet};

use chrono::{DateTime, Duration, Utc};
use fake::{Dummy, Fake, Faker};
use rand::prelude::SliceRandom;
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};

use crate::distributions;
use crate::domain::{ApiKey, AuditEvent, Dataset, Invitation, Membership, Organization, Project, User};
use crate::pools::{base_time, between, bounded_past, build_graph, deterministic_uuid, slugify, timezone_for_locale};
use crate::profiles::Profile;

const EDGE_CASE_NAMES: [&str; 5] = [
    "Sofie D'Aubigne",
    "Bjorn Asmussen",
    "Francois L'Ecuyer",
    "Marta Nunez de la Pena",
    "Zoe Kruger-Renaud",
];
const KEY_ALPHABET: &[u8] = b"abcdefghijklmnopqrstuvwxyz0123456789";

#[derive(Debug, Clone, Dummy)]
pub struct AddressSnapshot {
    pub city: String,
    pub country: String,
}

pub struct PipelineBuilder {
    pub profile: Profile,
    pub rng: StdRng,
    pub org_pool: Vec<Organization>,
    pub user_pool: Vec<User>,
    pub membership_pool: Vec<Membership>,
    pub project_pool: Vec<Project>,
    pub api_key_pool: Vec<ApiKey>,
    pub invitation_pool: Vec<Invitation>,
    pub audit_event_pool: Vec<AuditEvent>,
    pub org_member_map: HashMap<String, Vec<String>>,
}

impl PipelineBuilder {
    pub fn new(profile: Profile) -> Self {
        Self {
            profile,
            rng: StdRng::seed_from_u64(profile.seed),
            org_pool: Vec::new(),
            user_pool: Vec::new(),
            membership_pool: Vec::new(),
            project_pool: Vec::new(),
            api_key_pool: Vec::new(),
            invitation_pool: Vec::new(),
            audit_event_pool: Vec::new(),
            org_member_map: HashMap::new(),
        }
    }

    pub fn build_all(mut self) -> Self {
        self.build_orgs()
            .build_users()
            .build_memberships()
            .build_projects()
            .build_api_keys()
            .build_invitations()
            .build_audit_events();
        self
    }

    pub fn build_orgs(&mut self) -> &mut Self {
        let mut seen_slugs = HashSet::new();
        let mut seen_emails = HashSet::new();
        for index in 0..self.profile.num_orgs {
            let name: String = Faker.fake_with_rng(&mut self.rng);
            let display_name = format!("{} Labs {}", trim_title(&name), index + 1);
            let base_slug = slugify(&display_name);
            let mut slug = base_slug.clone();
            let mut suffix = 1;
            while seen_slugs.contains(&slug) {
                suffix += 1;
                slug = format!("{base_slug}-{suffix}");
            }
            seen_slugs.insert(slug.clone());
            let owner_email = unique_email(
                &mut self.rng,
                &mut seen_emails,
                &format!("owner{}", index + 1),
                "tenantcore-example.test",
            );
            self.org_pool.push(Organization {
                id: deterministic_uuid(&mut self.rng),
                name: display_name,
                slug,
                plan: distributions::weighted_plan(&mut self.rng).to_string(),
                region: distributions::weighted_region(&mut self.rng).to_string(),
                created_at: bounded_past(&mut self.rng, 365 * 3),
                owner_email,
            });
        }
        self
    }

    pub fn build_users(&mut self) -> &mut Self {
        let mut seen_emails = HashSet::new();
        for index in 0..self.profile.num_users {
            let locale = distributions::weighted_locale(&mut self.rng).to_string();
            let edge_case = self.rng.gen_bool(0.05);
            let _snapshot: AddressSnapshot = Faker.fake_with_rng(&mut self.rng);
            let local_part = if edge_case {
                format!("edgecase{:03}", index)
            } else {
                let base: String = Faker.fake_with_rng(&mut self.rng);
                slugify(&base)
            };
            let email = unique_email(
                &mut self.rng,
                &mut seen_emails,
                &local_part,
                &format!("{}.tenantcore-example.test", locale.to_lowercase().replace('-', "")),
            );
            let full_name = if edge_case {
                EDGE_CASE_NAMES[index % EDGE_CASE_NAMES.len()].to_string()
            } else {
                trim_title(&format!("{} {}", Faker.fake_with_rng::<String, _>(&mut self.rng), Faker.fake_with_rng::<String, _>(&mut self.rng)))
            };
            self.user_pool.push(User {
                id: deterministic_uuid(&mut self.rng),
                email,
                full_name,
                locale: locale.clone(),
                timezone: if edge_case {
                    "UTC".to_string()
                } else {
                    timezone_for_locale(&locale).to_string()
                },
                created_at: bounded_past(&mut self.rng, 365 * 3),
            });
        }
        self
    }

    pub fn build_memberships(&mut self) -> &mut Self {
        for org in &self.org_pool {
            let count = distributions::member_count(&mut self.rng, self.user_pool.len());
            let mut indices: Vec<usize> = (0..self.user_pool.len()).collect();
            indices.shuffle(&mut self.rng);
            let member_indices = &indices[..count];
            let mut member_ids: Vec<String> = Vec::new();
            for (position, index) in member_indices.iter().enumerate() {
                let user = &self.user_pool[*index];
                let invited_by = if position == 0 {
                    None
                } else {
                    Some(member_ids[self.rng.gen_range(0..member_ids.len())].clone())
                };
                let role = if position == 0 {
                    "owner".to_string()
                } else {
                    distributions::weighted_membership_role(&mut self.rng).to_string()
                };
                member_ids.push(user.id.clone());
                self.membership_pool.push(Membership {
                    id: deterministic_uuid(&mut self.rng),
                    org_id: org.id.clone(),
                    user_id: user.id.clone(),
                    role,
                    joined_at: between(&mut self.rng, org.created_at, base_time()),
                    invited_by,
                });
            }
            self.org_member_map.insert(org.id.clone(), member_ids);
        }
        self
    }

    pub fn build_projects(&mut self) -> &mut Self {
        for org in &self.org_pool {
            let member_ids = self.org_member_map.get(&org.id).cloned().unwrap_or_default();
            for index in 0..distributions::project_count(&mut self.rng) {
                self.project_pool.push(Project {
                    id: deterministic_uuid(&mut self.rng),
                    org_id: org.id.clone(),
                    name: format!("{} Workspace {}", trim_title(&fake_word(&mut self.rng)), index + 1),
                    status: distributions::weighted_project_status(&mut self.rng).to_string(),
                    created_by: member_ids.choose(&mut self.rng).unwrap().clone(),
                    created_at: between(&mut self.rng, org.created_at, base_time()),
                });
            }
        }
        self
    }

    pub fn build_api_keys(&mut self) -> &mut Self {
        let mut seen_prefixes = HashSet::new();
        for org in &self.org_pool {
            let member_ids = self.org_member_map.get(&org.id).cloned().unwrap_or_default();
            for _ in 0..distributions::api_key_count(&mut self.rng) {
                let mut key_prefix = format!("tc_{}", random_key(&mut self.rng));
                while seen_prefixes.contains(&key_prefix) {
                    key_prefix = format!("tc_{}", random_key(&mut self.rng));
                }
                seen_prefixes.insert(key_prefix.clone());
                let created_at = between(&mut self.rng, org.created_at, base_time());
                let last_used_at = self
                    .rng
                    .gen_bool(0.7)
                    .then(|| between(&mut self.rng, created_at, base_time()));
                self.api_key_pool.push(ApiKey {
                    id: deterministic_uuid(&mut self.rng),
                    org_id: org.id.clone(),
                    created_by: member_ids.choose(&mut self.rng).unwrap().clone(),
                    name: format!("{} token", trim_title(&fake_word(&mut self.rng))),
                    key_prefix,
                    created_at,
                    last_used_at,
                });
            }
        }
        self
    }

    pub fn build_invitations(&mut self) -> &mut Self {
        for org in &self.org_pool {
            let member_ids = self.org_member_map.get(&org.id).cloned().unwrap_or_default();
            let member_emails: HashSet<String> = self
                .membership_pool
                .iter()
                .filter(|membership| membership.org_id == org.id)
                .filter_map(|membership| self.user_pool.iter().find(|user| user.id == membership.user_id))
                .map(|user| user.email.to_lowercase())
                .collect();
            for index in 0..distributions::invitation_count(&mut self.rng) {
                let mut invited_email = format!("invite{:03}-{}@tenantcore-example.test", index, slugify(&org.slug));
                while member_emails.contains(&invited_email) {
                    invited_email = format!(
                        "invite{:03}-{}-{}@tenantcore-example.test",
                        index,
                        slugify(&org.slug),
                        self.rng.gen_range(1..=999)
                    );
                }
                self.invitation_pool.push(Invitation {
                    id: deterministic_uuid(&mut self.rng),
                    org_id: org.id.clone(),
                    invited_email,
                    role: distributions::weighted_invitation_role(&mut self.rng).to_string(),
                    invited_by: member_ids.choose(&mut self.rng).unwrap().clone(),
                    expires_at: base_time() + Duration::days(self.rng.gen_range(1..=30)),
                    accepted_at: self
                        .rng
                        .gen_bool(0.4)
                        .then(|| base_time() - Duration::days(self.rng.gen_range(1..=180))),
                });
            }
        }
        self
    }

    pub fn build_audit_events(&mut self) -> &mut Self {
        let dataset = Dataset {
            profile_name: self.profile.name.to_string(),
            seed: self.profile.seed,
            organizations: self.org_pool.clone(),
            users: self.user_pool.clone(),
            memberships: self.membership_pool.clone(),
            projects: self.project_pool.clone(),
            audit_events: Vec::new(),
            api_keys: self.api_key_pool.clone(),
            invitations: self.invitation_pool.clone(),
        };
        let graph = build_graph(&dataset);
        for project in &self.project_pool {
            let member_ids = graph.org_member_map.get(&project.org_id).cloned().unwrap_or_default();
            let memberships = graph.memberships_by_org.get(&project.org_id).cloned().unwrap_or_default();
            let api_keys = graph.api_keys_by_org.get(&project.org_id).cloned().unwrap_or_default();
            let invitations = graph
                .invitations_by_org
                .get(&project.org_id)
                .cloned()
                .unwrap_or_default();
            for _ in 0..distributions::audit_event_count(&mut self.rng, &project.status) {
                let user_id = member_ids.choose(&mut self.rng).unwrap().clone();
                let membership = graph
                    .membership_by_org_user
                    .get(&format!("{}:{}", project.org_id, user_id))
                    .unwrap();
                let floor = max_datetime(project.created_at, membership.joined_at);
                let resource_type = distributions::weighted_resource_type(&mut self.rng).to_string();
                let (final_type, resource_id) = match resource_type.as_str() {
                    "user" => ("user".to_string(), user_id.clone()),
                    "membership" => (
                        "membership".to_string(),
                        memberships.choose(&mut self.rng).unwrap().id.clone(),
                    ),
                    "api_key" if !api_keys.is_empty() => (
                        "api_key".to_string(),
                        api_keys.choose(&mut self.rng).unwrap().id.clone(),
                    ),
                    "invitation" if !invitations.is_empty() => (
                        "invitation".to_string(),
                        invitations.choose(&mut self.rng).unwrap().id.clone(),
                    ),
                    _ => ("project".to_string(), project.id.clone()),
                };
                self.audit_event_pool.push(AuditEvent {
                    id: deterministic_uuid(&mut self.rng),
                    org_id: project.org_id.clone(),
                    user_id,
                    project_id: project.id.clone(),
                    action: distributions::weighted_audit_action(&mut self.rng).to_string(),
                    resource_type: final_type,
                    resource_id,
                    ts: between(&mut self.rng, floor, base_time()),
                });
            }
        }
        self.audit_event_pool.sort_by_key(|event| event.ts);
        self
    }

    pub fn build(self) -> Dataset {
        Dataset {
            profile_name: self.profile.name.to_string(),
            seed: self.profile.seed,
            organizations: self.org_pool,
            users: self.user_pool,
            memberships: self.membership_pool,
            projects: self.project_pool,
            audit_events: self.audit_event_pool,
            api_keys: self.api_key_pool,
            invitations: self.invitation_pool,
        }
    }
}

fn unique_email(
    rng: &mut StdRng,
    seen: &mut HashSet<String>,
    local_hint: &str,
    domain: &str,
) -> String {
    let mut candidate = format!("{}@{}", slugify(local_hint), domain);
    while seen.contains(&candidate) {
        candidate = format!("{}{}@{}", slugify(local_hint), rng.gen_range(1..=9999), domain);
    }
    seen.insert(candidate.clone());
    candidate
}

fn fake_word(rng: &mut StdRng) -> String {
    let value: String = Faker.fake_with_rng(rng);
    slugify(&value).replace('-', "")
}

fn trim_title(value: &str) -> String {
    let compact = value
        .split_whitespace()
        .filter(|part| !part.is_empty())
        .take(3)
        .collect::<Vec<_>>()
        .join(" ");
    if compact.is_empty() {
        "Tenant".to_string()
    } else {
        compact
    }
}

fn random_key(rng: &mut StdRng) -> String {
    (0..8)
        .map(|_| KEY_ALPHABET[rng.gen_range(0..KEY_ALPHABET.len())] as char)
        .collect()
}

fn max_datetime(left: DateTime<Utc>, right: DateTime<Utc>) -> DateTime<Utc> {
    if left > right {
        left
    } else {
        right
    }
}
