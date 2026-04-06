use std::path::PathBuf;

use anyhow::{anyhow, Result};

use crate::cli::output;
use crate::core::filters::{filter_jobs, sort_jobs};
use crate::core::loader::{default_fixtures_path, load_config, load_events, load_jobs};
use crate::core::stats::compute_stats;
use crate::tui::app::run_app;
use crate::{Args, Command};

fn fixtures_path(cli_path: Option<PathBuf>) -> PathBuf {
    cli_path.unwrap_or_else(default_fixtures_path)
}

fn print_error(error: &anyhow::Error) {
    output::marker_block("## BEGIN_ERROR ##", &error.to_string(), "## END_ERROR ##");
}

pub fn run(args: Args) -> Result<()> {
    match args.command {
        Command::List(command) => {
            let items = load_jobs(&fixtures_path(args.fixtures_path)).map(|jobs| {
                sort_jobs(&filter_jobs(
                    &jobs,
                    command.status.as_deref(),
                    command.tag.as_deref(),
                ))
            });
            match items {
                Ok(jobs) => {
                    if command.output == "json" {
                        output::print_json(&jobs)
                    } else {
                        output::marker_block(
                            "## BEGIN_JOBS ##",
                            &output::jobs_table(&jobs),
                            "## END_JOBS ##",
                        );
                        Ok(())
                    }
                }
                Err(error) => {
                    print_error(&error.into());
                    Err(anyhow!("failed to list jobs"))
                }
            }
        }
        Command::Inspect(command) => {
            let jobs = match load_jobs(&fixtures_path(args.fixtures_path)) {
                Ok(items) => items,
                Err(error) => {
                    print_error(&error.into());
                    return Err(anyhow!("failed to inspect job"));
                }
            };
            let Some(job) = jobs.into_iter().find(|item| item.id == command.job_id) else {
                let error = anyhow!("job not found: {}", command.job_id);
                print_error(&error);
                return Err(error);
            };
            if command.output == "json" {
                output::print_json(&job)
            } else {
                output::marker_block(
                    "## BEGIN_JOB_DETAIL ##",
                    &output::job_plain(&job),
                    "## END_JOB_DETAIL ##",
                );
                Ok(())
            }
        }
        Command::Stats(command) => {
            let jobs = match load_jobs(&fixtures_path(args.fixtures_path)) {
                Ok(items) => items,
                Err(error) => {
                    print_error(&error.into());
                    return Err(anyhow!("failed to load stats"));
                }
            };
            let stats = compute_stats(&jobs);
            if command.output == "json" {
                output::print_json(&stats)
            } else {
                output::marker_block(
                    "## BEGIN_STATS ##",
                    &output::stats_plain(&stats),
                    "## END_STATS ##",
                );
                Ok(())
            }
        }
        Command::Watch(command) => {
            let root = fixtures_path(args.fixtures_path);
            let jobs = match load_jobs(&root) {
                Ok(items) => items,
                Err(error) => {
                    print_error(&error.into());
                    return Err(anyhow!("failed to watch jobs"));
                }
            };
            if command.no_tui {
                output::marker_block(
                    "## BEGIN_JOBS ##",
                    &output::jobs_table(&sort_jobs(&jobs)),
                    "## END_JOBS ##",
                );
                return Ok(());
            }
            let events = load_events(&root)?;
            let _config = load_config(&root)?;
            run_app(jobs, events, command.interval)
        }
    }
}
