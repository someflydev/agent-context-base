mod cli;
mod core;
mod tui;

use std::path::PathBuf;

use anyhow::Result;
use argh::FromArgs;

#[derive(FromArgs, Debug)]
/// TaskFlow Monitor
struct Args {
    #[argh(option)]
    /// path to the shared fixture corpus
    fixtures_path: Option<PathBuf>,

    #[argh(subcommand)]
    command: Command,
}

#[derive(FromArgs, Debug)]
#[argh(subcommand)]
enum Command {
    List(ListCommand),
    Inspect(InspectCommand),
    Stats(StatsCommand),
    Watch(WatchCommand),
}

#[derive(FromArgs, Debug)]
#[argh(subcommand, name = "list")]
/// list jobs
struct ListCommand {
    #[argh(option)]
    /// optional status filter
    status: Option<String>,
    #[argh(option)]
    /// optional tag filter
    tag: Option<String>,
    #[argh(option, default = "String::from(\"table\")")]
    /// output format: json or table
    output: String,
}

#[derive(FromArgs, Debug)]
#[argh(subcommand, name = "inspect")]
/// inspect a single job
struct InspectCommand {
    #[argh(positional)]
    job_id: String,
    #[argh(option, default = "String::from(\"plain\")")]
    /// output format: json or plain
    output: String,
}

#[derive(FromArgs, Debug)]
#[argh(subcommand, name = "stats")]
/// print job stats
struct StatsCommand {
    #[argh(option, default = "String::from(\"plain\")")]
    /// output format: json or plain
    output: String,
}

#[derive(FromArgs, Debug)]
#[argh(subcommand, name = "watch")]
/// run the dashboard
struct WatchCommand {
    #[argh(option, default = "5")]
    /// refresh interval in seconds
    interval: u64,
    #[argh(switch)]
    /// print a non-interactive snapshot instead of opening the TUI
    no_tui: bool,
}

fn main() -> Result<()> {
    cli::commands::run(argh::from_env())
}
