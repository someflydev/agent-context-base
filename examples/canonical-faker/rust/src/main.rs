mod distributions;
mod domain;
mod pipeline;
mod pools;
mod profiles;
mod validate;

use std::env;
use std::path::PathBuf;

use pipeline::PipelineBuilder;
use pools::write_jsonl;
use profiles::Profile;
use validate::validate;

fn main() {
    let mut profile_name = "smoke".to_string();
    let mut output_dir = PathBuf::from("./output");
    let mut format = "jsonl".to_string();
    let mut seed_override = None;

    let mut args = env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--profile" => profile_name = args.next().unwrap_or_else(|| "smoke".to_string()),
            "--output" => output_dir = PathBuf::from(args.next().unwrap_or_else(|| "./output".to_string())),
            "--format" => format = args.next().unwrap_or_else(|| "jsonl".to_string()),
            "--seed" => seed_override = args.next().and_then(|value| value.parse::<u64>().ok()),
            _ => {}
        }
    }

    let profile = Profile::resolve(&profile_name, seed_override);
    let dataset = PipelineBuilder::new(profile).build_all().build();
    let report = validate(&dataset);
    println!("{}", serde_json::to_string_pretty(&report).unwrap());
    if !report.ok {
        std::process::exit(1);
    }
    if format != "jsonl" {
        eprintln!("only jsonl output is implemented in the canonical Rust example");
        std::process::exit(1);
    }
    let target_dir = output_dir.join(profile.name);
    if let Err(err) = write_jsonl(&dataset, &target_dir, &report) {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
