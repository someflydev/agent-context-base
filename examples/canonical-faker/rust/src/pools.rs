use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::Path;

use chrono::{DateTime, SecondsFormat, TimeZone, Utc};
use rand::rngs::StdRng;
use rand::Rng;
use serde::Serialize;
use uuid::Builder;

use crate::domain::{ApiKey, AuditEvent, Dataset, Invitation, Membership, Project};
use crate::validate::ValidationReport;

pub const BASE_TIME_STR: &str = "2026-01-01T12:00:00Z";

pub fn base_time() -> DateTime<Utc> {
    Utc.with_ymd_and_hms(2026, 1, 1, 12, 0, 0).unwrap()
}

pub fn iso(value: DateTime<Utc>) -> String {
    value.to_rfc3339_opts(SecondsFormat::Secs, true)
}

pub fn timezone_for_locale(locale: &str) -> &'static str {
    match locale {
        "en-GB" => "Europe/London",
        "de-DE" => "Europe/Berlin",
        "fr-FR" => "Europe/Paris",
        _ => "America/New_York",
    }
}

pub fn slugify(value: &str) -> String {
    let mut slug = String::new();
    let mut last_dash = false;
    for ch in value.chars() {
        if ch.is_ascii_alphanumeric() {
            slug.push(ch.to_ascii_lowercase());
            last_dash = false;
        } else if !last_dash {
            slug.push('-');
            last_dash = true;
        }
    }
    slug.trim_matches('-').to_string()
}

pub fn deterministic_uuid(rng: &mut StdRng) -> String {
    let mut bytes = [0_u8; 16];
    rng.fill(&mut bytes);
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    Builder::from_random_bytes(bytes).into_uuid().to_string()
}

pub fn bounded_past(rng: &mut StdRng, earliest_days_ago: i64) -> DateTime<Utc> {
    base_time() - chrono::Duration::days(rng.gen_range(0..=earliest_days_ago))
}

pub fn between(rng: &mut StdRng, floor: DateTime<Utc>, ceiling: DateTime<Utc>) -> DateTime<Utc> {
    let start = floor.timestamp();
    let end = ceiling.timestamp();
    if start >= end {
        return floor;
    }
    Utc.timestamp_opt(rng.gen_range(start..=end), 0).unwrap()
}

pub fn write_jsonl(dataset: &Dataset, output_dir: &Path, report: &ValidationReport) -> std::io::Result<()> {
    fs::create_dir_all(output_dir)?;
    write_entity(&output_dir.join("organizations.jsonl"), &dataset.organizations)?;
    write_entity(&output_dir.join("users.jsonl"), &dataset.users)?;
    write_entity(&output_dir.join("memberships.jsonl"), &dataset.memberships)?;
    write_entity(&output_dir.join("projects.jsonl"), &dataset.projects)?;
    write_entity(&output_dir.join("audit_events.jsonl"), &dataset.audit_events)?;
    write_entity(&output_dir.join("api_keys.jsonl"), &dataset.api_keys)?;
    write_entity(&output_dir.join("invitations.jsonl"), &dataset.invitations)?;
    let report_file = File::create(output_dir.join(format!("{}-report.json", dataset.profile_name)))?;
    serde_json::to_writer_pretty(report_file, report)?;
    Ok(())
}

fn write_entity<T: Serialize>(path: &Path, rows: &[T]) -> std::io::Result<()> {
    let mut writer = BufWriter::new(File::create(path)?);
    for row in rows {
        serde_json::to_writer(&mut writer, row)?;
        writer.write_all(b"\n")?;
    }
    writer.flush()
}

#[derive(Debug, Clone, Default)]
pub struct GraphPools {
    pub org_member_map: HashMap<String, Vec<String>>,
    pub user_email_by_id: HashMap<String, String>,
    pub membership_by_org_user: HashMap<String, Membership>,
    pub memberships_by_org: HashMap<String, Vec<Membership>>,
    pub projects_by_org: HashMap<String, Vec<Project>>,
    pub api_keys_by_org: HashMap<String, Vec<ApiKey>>,
    pub invitations_by_org: HashMap<String, Vec<Invitation>>,
    pub audit_events_by_org: HashMap<String, Vec<AuditEvent>>,
}

pub fn build_graph(dataset: &Dataset) -> GraphPools {
    let mut graph = GraphPools::default();
    for user in &dataset.users {
        graph
            .user_email_by_id
            .insert(user.id.clone(), user.email.to_lowercase());
    }
    for membership in &dataset.memberships {
        graph
            .org_member_map
            .entry(membership.org_id.clone())
            .or_default()
            .push(membership.user_id.clone());
        graph.membership_by_org_user.insert(
            format!("{}:{}", membership.org_id, membership.user_id),
            membership.clone(),
        );
        graph
            .memberships_by_org
            .entry(membership.org_id.clone())
            .or_default()
            .push(membership.clone());
    }
    for project in &dataset.projects {
        graph
            .projects_by_org
            .entry(project.org_id.clone())
            .or_default()
            .push(project.clone());
    }
    for api_key in &dataset.api_keys {
        graph
            .api_keys_by_org
            .entry(api_key.org_id.clone())
            .or_default()
            .push(api_key.clone());
    }
    for invitation in &dataset.invitations {
        graph
            .invitations_by_org
            .entry(invitation.org_id.clone())
            .or_default()
            .push(invitation.clone());
    }
    for audit_event in &dataset.audit_events {
        graph
            .audit_events_by_org
            .entry(audit_event.org_id.clone())
            .or_default()
            .push(audit_event.clone());
    }
    graph
}
