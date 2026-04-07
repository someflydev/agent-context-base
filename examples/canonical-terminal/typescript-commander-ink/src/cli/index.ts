#!/usr/bin/env node
import path from "node:path";
import { Command } from "commander";

import { filterJobs, sortJobs } from "../core/filters.js";
import { defaultFixturesPath, FixtureError, loadJobs } from "../core/loader.js";
import { computeStats } from "../core/stats.js";
import type { JobStatus } from "../core/models.js";
import { jobPlain, jobsTable, markerWrap, statsPlain } from "./output.js";
import { renderApp } from "../tui/App.js";

function resolveFixturesPath(fixturesPath?: string): string {
  return fixturesPath ? path.resolve(fixturesPath) : defaultFixturesPath();
}

async function withFixtures<T>(fixturesPath: string, work: () => Promise<T>): Promise<T> {
  try {
    return await work();
  } catch (error) {
    if (error instanceof FixtureError) {
      console.error(markerWrap("## BEGIN_ERROR ##", error.message, "## END_ERROR ##"));
      process.exitCode = 1;
      throw error;
    }
    throw error;
  }
}

const program = new Command();

program.name("taskflow").description("TaskFlow Monitor CLI");

program
  .option("--fixtures-path <path>", "Override fixture corpus path")
  .showHelpAfterError();

program
  .command("list")
  .option("--status <status>")
  .option("--tag <tag>")
  .option("--output <format>", "json or table", "table")
  .action(async (options, command) => {
    const fixturesPath = resolveFixturesPath(command.parent?.opts().fixturesPath);
    await withFixtures(fixturesPath, async () => {
      const jobs = sortJobs(
        filterJobs(await loadJobs(fixturesPath), {
          status: options.status as JobStatus | undefined,
          tag: options.tag as string | undefined,
        }),
      );
      if (options.output === "json") {
        console.log(JSON.stringify(jobs, null, 2));
        return;
      }
      console.log(markerWrap("## BEGIN_JOBS ##", jobsTable(jobs), "## END_JOBS ##"));
    });
  });

program
  .command("inspect")
  .argument("<jobId>")
  .option("--output <format>", "json or plain", "plain")
  .action(async (jobId: string, options, command) => {
    const fixturesPath = resolveFixturesPath(command.parent?.opts().fixturesPath);
    await withFixtures(fixturesPath, async () => {
      const job = (await loadJobs(fixturesPath)).find((item) => item.id === jobId);
      if (!job) {
        throw new FixtureError(`job not found: ${jobId}`);
      }
      if (options.output === "json") {
        console.log(JSON.stringify(job, null, 2));
        return;
      }
      console.log(markerWrap("## BEGIN_JOB_DETAIL ##", jobPlain(job), "## END_JOB_DETAIL ##"));
    });
  });

program
  .command("stats")
  .option("--output <format>", "json or plain", "plain")
  .action(async (options, command) => {
    const fixturesPath = resolveFixturesPath(command.parent?.opts().fixturesPath);
    await withFixtures(fixturesPath, async () => {
      const stats = computeStats(await loadJobs(fixturesPath));
      if (options.output === "json") {
        console.log(JSON.stringify(stats, null, 2));
        return;
      }
      console.log(markerWrap("## BEGIN_STATS ##", statsPlain(stats), "## END_STATS ##"));
    });
  });

program
  .command("watch")
  .option("--interval <seconds>", "Refresh interval in seconds", "5")
  .option("--no-tui", "Render once and exit without TUI")
  .action(async (options, command) => {
    const fixturesPath = resolveFixturesPath(command.parent?.opts().fixturesPath);
    await withFixtures(fixturesPath, async () => {
      const jobs = sortJobs(await loadJobs(fixturesPath));
      if (options.noTui || !process.stdout.isTTY) {
        console.log(markerWrap("## BEGIN_JOBS ##", jobsTable(jobs), "## END_JOBS ##"));
        return;
      }
      renderApp(fixturesPath);
    });
  });

program.parseAsync(process.argv).catch((error) => {
  if (error instanceof FixtureError) {
    return;
  }
  console.error(error);
  process.exit(1);
});
