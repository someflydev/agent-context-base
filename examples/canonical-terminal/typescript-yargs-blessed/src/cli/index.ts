#!/usr/bin/env node
import path from "node:path";

import yargs from "yargs";
import { hideBin } from "yargs/helpers";

import { filterJobs, sortJobs } from "../core/filters.js";
import { defaultFixturesPath, FixtureError, loadJobs } from "../core/loader.js";
import { computeStats } from "../core/stats.js";
import type { JobStatus } from "../core/models.js";
import { jobPlain, jobsTable, markerWrap, statsPlain } from "./output.js";
import { runTui } from "../tui/app.js";

function resolveFixturesPath(value?: string): string {
  return value ? path.resolve(value) : defaultFixturesPath();
}

function failWithError(error: unknown): never {
  const message = error instanceof Error ? error.message : String(error);
  console.error(markerWrap("## BEGIN_ERROR ##", message, "## END_ERROR ##"));
  process.exit(1);
}

await yargs(hideBin(process.argv))
  .scriptName("taskflow")
  .option("fixtures-path", {
    type: "string",
    default: defaultFixturesPath(),
  })
  .command(
    "list",
    "List jobs",
    (command) =>
      command
        .option("status", { type: "string" })
        .option("tag", { type: "string" })
        .option("output", { choices: ["json", "table"] as const, default: "table" }),
    async (argv) => {
      try {
        const jobs = sortJobs(filterJobs(await loadJobs(resolveFixturesPath(argv.fixturesPath)), argv.status as JobStatus | undefined, argv.tag));
        if (argv.output === "json") {
          console.log(JSON.stringify(jobs, null, 2));
          return;
        }
        console.log(markerWrap("## BEGIN_JOBS ##", jobsTable(jobs), "## END_JOBS ##"));
      } catch (error) {
        failWithError(error);
      }
    },
  )
  .command(
    "inspect <jobId>",
    "Inspect a job",
    (command) => command.positional("jobId", { type: "string" }).option("output", { choices: ["json", "plain"] as const, default: "plain" }),
    async (argv) => {
      try {
        const job = (await loadJobs(resolveFixturesPath(argv.fixturesPath))).find((item) => item.id === argv.jobId);
        if (!job) {
          throw new FixtureError(`job not found: ${argv.jobId}`);
        }
        if (argv.output === "json") {
          console.log(JSON.stringify(job, null, 2));
          return;
        }
        console.log(markerWrap("## BEGIN_JOB_DETAIL ##", jobPlain(job), "## END_JOB_DETAIL ##"));
      } catch (error) {
        failWithError(error);
      }
    },
  )
  .command(
    "stats",
    "Print aggregate stats",
    (command) => command.option("output", { choices: ["json", "plain"] as const, default: "plain" }),
    async (argv) => {
      try {
        const stats = computeStats(await loadJobs(resolveFixturesPath(argv.fixturesPath)));
        if (argv.output === "json") {
          console.log(JSON.stringify(stats, null, 2));
          return;
        }
        console.log(markerWrap("## BEGIN_STATS ##", statsPlain(stats), "## END_STATS ##"));
      } catch (error) {
        failWithError(error);
      }
    },
  )
  .command(
    "watch",
    "Watch jobs",
    (command) => command.option("interval", { type: "number", default: 5 }).option("tui", { type: "boolean", default: true }),
    async (argv) => {
      void argv.interval;
      try {
        const fixturesPath = resolveFixturesPath(argv.fixturesPath);
        const jobs = sortJobs(await loadJobs(fixturesPath));
        if (!argv.tui || !process.stdout.isTTY) {
          console.log(markerWrap("## BEGIN_JOBS ##", jobsTable(jobs), "## END_JOBS ##"));
          return;
        }
        await runTui(fixturesPath);
      } catch (error) {
        failWithError(error);
      }
    },
  )
  .demandCommand()
  .strict()
  .parseAsync();
