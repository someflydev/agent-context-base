import path from "node:path";

import { describe, expect, test } from "vitest";

import { filterJobs } from "../../src/core/filters.js";
import { defaultFixturesPath, loadConfig, loadEvents, loadJobs } from "../../src/core/loader.js";
import { computeStats } from "../../src/core/stats.js";

describe("taskflow core", () => {
  test("loads fixtures", async () => {
    const fixturesPath = defaultFixturesPath();
    const [jobs, events, config] = await Promise.all([loadJobs(fixturesPath), loadEvents(fixturesPath), loadConfig(fixturesPath)]);
    expect(jobs).toHaveLength(20);
    expect(events.length).toBeGreaterThanOrEqual(40);
    expect(config.queue_name).toBe("taskflow-ci");
  });

  test("filters jobs by status and tag", async () => {
    const jobs = await loadJobs(defaultFixturesPath());
    expect(filterJobs(jobs, { status: "done" }).every((job) => job.status === "done")).toBe(true);
    expect(filterJobs(jobs, { tag: "frontend" }).length).toBeGreaterThan(0);
  });

  test("computes stats", async () => {
    const jobs = await loadJobs(path.resolve(defaultFixturesPath()));
    const stats = computeStats(jobs);
    expect(stats.total).toBe(20);
    expect(stats.by_status.done).toBeGreaterThan(0);
  });
});
