use std::path::PathBuf;

use anyhow::{anyhow, Result};

use crate::cli::output;
use crate::core::filters::{filter_jobs, sort_jobs};
use crate::core::loader::{default_fixtures_path, load_config, load_events, load_jobs};
use crate::core::stats::compute_stats;
use crate::tui::app::run_app;
use crate::{Args, Command, OutputFormat};

fn fixtures_path(cli_path: Option<PathBuf>) -> PathBuf {
    cli_path.unwrap_or_else(default_fixtures_path)
}

fn print_error(error: &anyhow::Error) {
    output::marker_block("## BEGIN_ERROR ##", &error.to_string(), "## END_ERROR ##");
}

pub fn run(args: Args) -> Result<()> {
    match args.command {
        Command::List {
            status,
            tag,
            output,
        } => {
            let jobs = load_jobs(&fixtures_path(args.fixtures_path))
                .map(|items| sort_jobs(&filter_jobs(&items, status.as_deref(), tag.as_deref())));
            match jobs {
                Ok(items) => match output {
                    OutputFormat::Json => output::print_json(&items),
                    OutputFormat::Table | OutputFormat::Plain => {
                        output::marker_block(
                            "## BEGIN_JOBS ##",
                            &output::jobs_table(&items),
                            "## END_JOBS ##",
                        );
                        Ok(())
                    }
                },
                Err(error) => {
                    print_error(&error.into());
                    Err(anyhow!("failed to list jobs"))
                }
            }
        }
        Command::Inspect { job_id, output } => {
            let jobs = match load_jobs(&fixtures_path(args.fixtures_path)) {
                Ok(items) => items,
                Err(error) => {
                    print_error(&error.into());
                    return Err(anyhow!("failed to inspect job"));
                }
            };
            let Some(job) = jobs.into_iter().find(|item| item.id == job_id) else {
                let error = anyhow!("job not found: {job_id}");
                print_error(&error);
                return Err(error);
            };
            match output {
                OutputFormat::Json => output::print_json(&job),
                OutputFormat::Table | OutputFormat::Plain => {
                    output::marker_block(
                        "## BEGIN_JOB_DETAIL ##",
                        &output::job_plain(&job),
                        "## END_JOB_DETAIL ##",
                    );
                    Ok(())
                }
            }
        }
        Command::Stats { output } => {
            let jobs = match load_jobs(&fixtures_path(args.fixtures_path)) {
                Ok(items) => items,
                Err(error) => {
                    print_error(&error.into());
                    return Err(anyhow!("failed to load stats fixtures"));
                }
            };
            let stats = compute_stats(&jobs);
            match output {
                OutputFormat::Json => output::print_json(&stats),
                OutputFormat::Table | OutputFormat::Plain => {
                    output::marker_block(
                        "## BEGIN_STATS ##",
                        &output::stats_plain(&stats),
                        "## END_STATS ##",
                    );
                    Ok(())
                }
            }
        }
        Command::Watch { interval, no_tui } => {
            let fixture_root = fixtures_path(args.fixtures_path);
            let jobs = match load_jobs(&fixture_root) {
                Ok(items) => items,
                Err(error) => {
                    print_error(&error.into());
                    return Err(anyhow!("failed to watch jobs"));
                }
            };
            if no_tui {
                output::marker_block(
                    "## BEGIN_JOBS ##",
                    &output::jobs_table(&sort_jobs(&jobs)),
                    "## END_JOBS ##",
                );
                return Ok(());
            }
            let events = load_events(&fixture_root)?;
            let _config = load_config(&fixture_root)?;
            run_app(jobs, events, interval)
        }
    }
}
