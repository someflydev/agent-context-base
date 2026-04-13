use rand::prelude::SliceRandom;
use rand::Rng;

pub fn weighted_plan(rng: &mut impl Rng) -> &'static str {
    [
        "free",
        "free",
        "free",
        "free",
        "free",
        "pro",
        "pro",
        "pro",
        "pro",
        "enterprise",
    ]
    .choose(rng)
    .copied()
    .unwrap()
}

pub fn weighted_region(rng: &mut impl Rng) -> &'static str {
    [
        "us-east",
        "us-east",
        "us-east",
        "us-east",
        "us-west",
        "us-west",
        "eu-west",
        "eu-west",
        "ap-southeast",
    ]
    .choose(rng)
    .copied()
    .unwrap()
}

pub fn weighted_locale(rng: &mut impl Rng) -> &'static str {
    [
        "en-US", "en-US", "en-US", "en-US", "en-US", "en-US", "en-GB", "en-GB", "de-DE",
        "fr-FR",
    ]
    .choose(rng)
    .copied()
    .unwrap()
}

pub fn weighted_membership_role(rng: &mut impl Rng) -> &'static str {
    [
        "admin", "member", "member", "member", "member", "member", "member", "viewer",
        "viewer", "viewer",
    ]
    .choose(rng)
    .copied()
    .unwrap()
}

pub fn weighted_project_status(rng: &mut impl Rng) -> &'static str {
    [
        "active",
        "active",
        "active",
        "active",
        "active",
        "active",
        "archived",
        "archived",
        "draft",
        "draft",
    ]
    .choose(rng)
    .copied()
    .unwrap()
}

pub fn weighted_invitation_role(rng: &mut impl Rng) -> &'static str {
    ["admin", "member", "member", "member", "viewer", "viewer"]
        .choose(rng)
        .copied()
        .unwrap()
}

pub fn weighted_audit_action(rng: &mut impl Rng) -> &'static str {
    [
        "created",
        "created",
        "updated",
        "updated",
        "updated",
        "deleted",
        "archived",
        "invited",
        "exported",
    ]
    .choose(rng)
    .copied()
    .unwrap()
}

pub fn weighted_resource_type(rng: &mut impl Rng) -> &'static str {
    [
        "project",
        "project",
        "project",
        "user",
        "membership",
        "membership",
        "api_key",
        "invitation",
    ]
    .choose(rng)
    .copied()
    .unwrap()
}

pub fn member_count(rng: &mut impl Rng, user_count: usize) -> usize {
    let max_count = user_count.min(8).max(3);
    rng.gen_range(3..=max_count)
}

pub fn project_count(rng: &mut impl Rng) -> usize {
    rng.gen_range(2..=4)
}

pub fn api_key_count(rng: &mut impl Rng) -> usize {
    rng.gen_range(1..=2)
}

pub fn invitation_count(rng: &mut impl Rng) -> usize {
    rng.gen_range(1..=2)
}

pub fn audit_event_count(rng: &mut impl Rng, status: &str) -> usize {
    match status {
        "active" => rng.gen_range(8..=14),
        "archived" => rng.gen_range(4..=8),
        _ => rng.gen_range(3..=5),
    }
}
