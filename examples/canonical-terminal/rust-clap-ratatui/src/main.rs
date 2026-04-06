mod cli;
mod core;
mod tui;

use std::path::PathBuf;

use anyhow::Result;
use clap::{Parser, Subcommand, ValueEnum};

#[derive(Debug, Clone, ValueEnum)]
enum OutputFormat {
    Json,
    Table,
    Plain,
}

#[derive(Debug, Parser)]
#[command(name = "taskflow", about = "TaskFlow Monitor")]
struct Args {
    #[arg(long, global = true)]
    fixtures_path: Option<PathBuf>,
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    List {
        #[arg(long)]
        status: Option<String>,
        #[arg(long)]
        tag: Option<String>,
        #[arg(long, value_enum, default_value = "table")]
        output: OutputFormat,
    },
    Inspect {
        job_id: String,
        #[arg(long, value_enum, default_value = "plain")]
        output: OutputFormat,
    },
    Stats {
        #[arg(long, value_enum, default_value = "plain")]
        output: OutputFormat,
    },
    Watch {
        #[arg(long, default_value_t = 5)]
        interval: u64,
        #[arg(long, default_value_t = false)]
        no_tui: bool,
    },
}

fn main() -> Result<()> {
    let args = Args::parse();
    cli::commands::run(args)
}
