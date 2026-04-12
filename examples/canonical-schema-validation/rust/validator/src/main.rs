mod models;

use std::{fs, path::PathBuf};

use models::{validate_cross_fields_sync_run, validate_workspace_plan, SyncRun, WorkspaceConfig};
use serde::de::DeserializeOwned;
use validator::Validate;

fn load_fixture<T: DeserializeOwned>(name: &str) -> T {
    let path = PathBuf::from("../../domain/fixtures").join(name);
    let text = fs::read_to_string(path).expect("fixture should exist");
    serde_json::from_str(&text).expect("fixture should deserialize")
}

fn main() {
    let valid_workspace: WorkspaceConfig = load_fixture("valid/workspace_config_basic.json");
    match valid_workspace
        .validate()
        .and_then(|_| validate_workspace_plan(&valid_workspace))
    {
        Ok(_) => println!("valid workspace PASS"),
        Err(err) => {
            eprintln!("valid workspace FAIL: {err}");
            std::process::exit(1);
        }
    }

    let invalid_slug: WorkspaceConfig = load_fixture("invalid/workspace_config_bad_slug.json");
    if invalid_slug.validate().is_ok() {
        eprintln!("invalid slug fixture unexpectedly passed");
        std::process::exit(1);
    }
    println!("invalid slug FAIL as expected");

    let invalid_sync: SyncRun = load_fixture("invalid/sync_run_timestamps_inverted.json");
    if invalid_sync.validate().is_ok() && validate_cross_fields_sync_run(&invalid_sync).is_ok() {
        eprintln!("invalid sync fixture unexpectedly passed");
        std::process::exit(1);
    }
    println!("invalid sync FAIL as expected");
}
