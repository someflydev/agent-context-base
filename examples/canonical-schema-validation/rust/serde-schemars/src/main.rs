mod models;
mod schema_export;

use std::{fs, path::PathBuf};

use schema_export::{compile_schema, export_workspace_config_schema};
use serde_json::Value;

fn load_value(name: &str) -> Value {
    let path = PathBuf::from("../../domain/fixtures").join(name);
    let text = fs::read_to_string(path).expect("fixture should exist");
    serde_json::from_str(&text).expect("fixture should parse")
}

fn main() {
    let schema_json = export_workspace_config_schema();
    println!("{schema_json}");

    fs::write("workspace_config.schema.json", &schema_json).expect("schema file should write");
    let validator = compile_schema(&schema_json);

    let valid = load_value("valid/workspace_config_full.json");
    if validator.validate(&valid).is_err() {
        eprintln!("valid fixture failed schema validation");
        std::process::exit(1);
    }

    let invalid = load_value("invalid/workspace_config_bad_slug.json");
    if validator.validate(&invalid).is_ok() {
        eprintln!("invalid fixture unexpectedly passed schema validation");
        std::process::exit(1);
    }

    println!("schema export and drift checks passed");
}
