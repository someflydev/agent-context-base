mod models;

use std::{fs, path::PathBuf};

use garde::Validate;
use models::{
    validate_sync_cross_fields, validate_workspace_cross_fields, SyncRun, WorkspaceConfig,
};
use serde::de::DeserializeOwned;

fn load_fixture<T: DeserializeOwned>(name: &str) -> T {
    let path = PathBuf::from("../../domain/fixtures").join(name);
    let text = fs::read_to_string(path).expect("fixture should exist");
    serde_json::from_str(&text).expect("fixture should deserialize")
}

fn main() {
    let valid: WorkspaceConfig = load_fixture("valid/workspace_config_basic.json");
    valid.validate().expect("valid workspace should pass garde");
    validate_workspace_cross_fields(&valid).expect("valid workspace should satisfy plan limits");

    let invalid: WorkspaceConfig = load_fixture("invalid/workspace_config_bad_slug.json");
    if invalid.validate().is_ok() {
        eprintln!("invalid slug fixture unexpectedly passed");
        std::process::exit(1);
    }

    let sync_invalid: SyncRun = load_fixture("invalid/sync_run_timestamps_inverted.json");
    sync_invalid
        .validate()
        .expect("field-level sync data should deserialize");
    if validate_sync_cross_fields(&sync_invalid).is_ok() {
        eprintln!("invalid sync fixture unexpectedly passed");
        std::process::exit(1);
    }

    println!("garde runtime checks passed");
}
