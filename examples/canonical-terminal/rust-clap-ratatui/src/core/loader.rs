use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use anyhow::{anyhow, Context, Result};

use crate::core::models::{Event, Job};

pub fn default_fixtures_path() -> PathBuf {
    if let Ok(value) = env::var("TASKFLOW_FIXTURES_PATH") {
        return PathBuf::from(value);
    }

    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let local = manifest_dir.join("fixtures");
    if local.exists() {
        return local;
    }

    manifest_dir
        .join("..")
        .join("fixtures")
        .canonicalize()
        .unwrap_or_else(|_| manifest_dir.join("..").join("fixtures"))
}

fn load_json<T: serde::de::DeserializeOwned>(fixtures_path: &Path, filename: &str) -> Result<T> {
    if !fixtures_path.exists() {
        return Err(anyhow!(
            "fixtures path does not exist: {}",
            fixtures_path.display()
        ));
    }
    let target = fixtures_path.join(filename);
    let raw = fs::read_to_string(&target)
        .with_context(|| format!("missing fixture file: {}", target.display()))?;
    serde_json::from_str(&raw).with_context(|| format!("failed to parse {}", target.display()))
}

pub fn load_jobs(fixtures_path: &Path) -> Result<Vec<Job>> {
    load_json(fixtures_path, "jobs.json")
}

pub fn load_events(fixtures_path: &Path) -> Result<Vec<Event>> {
    let mut events: Vec<Event> = load_json(fixtures_path, "events.json")?;
    events.sort_by(|left, right| left.timestamp.cmp(&right.timestamp));
    Ok(events)
}

pub fn load_config(fixtures_path: &Path) -> Result<serde_json::Value> {
    load_json(fixtures_path, "config.json")
}
