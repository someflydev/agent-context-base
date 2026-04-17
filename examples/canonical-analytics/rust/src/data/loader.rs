use super::models::{Deployment, Event, FunnelStage, Incident, LatencySample, Service, Session};
use serde::Deserialize;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Deserialize)]
pub struct FixtureStore {
    #[serde(default)]
    pub events: Vec<Event>,
    #[serde(default)]
    pub sessions: Vec<Session>,
    #[serde(default)]
    pub services: Vec<Service>,
    #[serde(default)]
    pub deployments: Vec<Deployment>,
    #[serde(default)]
    pub incidents: Vec<Incident>,
    #[serde(default)]
    pub latency_samples: Vec<LatencySample>,
    #[serde(default)]
    pub funnel_stages: Vec<FunnelStage>,
}

pub fn load_fixtures(path: &Path) -> anyhow::Result<FixtureStore> {
    let content = fs::read_to_string(path)?;
    let store: FixtureStore = serde_json::from_str(&content)?;
    Ok(store)
}

pub fn get_fixture_path() -> PathBuf {
    if let Ok(path) = env::var("FIXTURE_PATH") {
        PathBuf::from(path)
    } else {
        // Resolve relative to cargo manifest dir by default
        let manifest_dir = env::var("CARGO_MANIFEST_DIR")
            .unwrap_or_else(|_| ".".to_string());
        PathBuf::from(manifest_dir).join("../domain/fixtures/smoke.json")
    }
}
