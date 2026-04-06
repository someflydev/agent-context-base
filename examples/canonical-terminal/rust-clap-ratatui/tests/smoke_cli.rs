use std::path::PathBuf;
use std::process::Command;

fn fixtures_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("fixtures")
}

fn binary() -> &'static str {
    env!("CARGO_BIN_EXE_taskflow")
}

#[test]
fn list_table_output() {
    let output = Command::new(binary())
        .args(["--fixtures-path", fixtures_path().to_str().unwrap(), "list"])
        .output()
        .unwrap();
    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("## BEGIN_JOBS ##"));
    assert!(stdout.contains("## END_JOBS ##"));
}

#[test]
fn list_json() {
    let output = Command::new(binary())
        .args([
            "--fixtures-path",
            fixtures_path().to_str().unwrap(),
            "list",
            "--output",
            "json",
        ])
        .output()
        .unwrap();
    assert!(output.status.success());
    let payload: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(payload.as_array().unwrap().len(), 20);
}

#[test]
fn filter_by_status() {
    let output = Command::new(binary())
        .args([
            "--fixtures-path",
            fixtures_path().to_str().unwrap(),
            "list",
            "--status",
            "done",
            "--output",
            "json",
        ])
        .output()
        .unwrap();
    assert!(output.status.success());
    let payload: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    for job in payload.as_array().unwrap() {
        assert_eq!(job.get("status").unwrap(), "done");
    }
}

#[test]
fn inspect_job() {
    let output = Command::new(binary())
        .args([
            "--fixtures-path",
            fixtures_path().to_str().unwrap(),
            "inspect",
            "job-001",
            "--output",
            "json",
        ])
        .output()
        .unwrap();
    assert!(output.status.success());
    let payload: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(payload.get("id").unwrap(), "job-001");
}

#[test]
fn stats_json() {
    let output = Command::new(binary())
        .args([
            "--fixtures-path",
            fixtures_path().to_str().unwrap(),
            "stats",
            "--output",
            "json",
        ])
        .output()
        .unwrap();
    assert!(output.status.success());
    let payload: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(payload.get("total").unwrap(), 20);
}

#[test]
fn watch_no_tui() {
    let output = Command::new(binary())
        .args([
            "--fixtures-path",
            fixtures_path().to_str().unwrap(),
            "watch",
            "--no-tui",
        ])
        .output()
        .unwrap();
    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("## BEGIN_JOBS ##"));
}
