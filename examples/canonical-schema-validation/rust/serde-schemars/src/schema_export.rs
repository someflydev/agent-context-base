use jsonschema::JSONSchema;
use schemars::schema_for;
use serde_json::{json, Value};

use crate::models::WorkspaceConfig;

pub fn export_workspace_config_schema() -> String {
    let schema = schema_for!(WorkspaceConfig);
    let mut value = serde_json::to_value(&schema).expect("schema should convert to JSON");
    enrich_workspace_contract(&mut value);
    serde_json::to_string_pretty(&value).expect("schema should serialize")
}

pub fn compile_schema(schema_json: &str) -> JSONSchema {
    let schema: Value = serde_json::from_str(schema_json).expect("schema must be valid JSON");
    JSONSchema::compile(&schema).expect("schema should compile")
}

fn enrich_workspace_contract(schema: &mut Value) {
    let properties = &mut schema["properties"];
    properties["name"]["minLength"] = json!(3);
    properties["name"]["maxLength"] = json!(100);
    properties["slug"]["pattern"] = json!("^[a-z][a-z0-9-]{1,48}[a-z0-9]$");
    properties["owner_email"]["format"] = json!("email");
    properties["max_sync_runs"]["minimum"] = json!(1);
    properties["max_sync_runs"]["maximum"] = json!(1000);
    properties["created_at"]["format"] = json!("date-time");
    if let Some(settings) = schema["definitions"]["SettingsBlock"].as_object_mut() {
        settings.insert(
            "required".to_string(),
            json!([
                "notify_on_failure",
                "retry_max",
                "timeout_seconds",
                "webhook_url"
            ]),
        );
    }
}
