import { describe, expect, test } from "vitest";

import { filterJobs } from "../../src/core/filters.js";
import { defaultFixturesPath, loadConfig, loadEvents, loadJobs } from "../../src/core/loader.js";
import { computeStats } from "../../src/core/stats.js";

describe("taskflow core", () => {
  test("loads shared fixtures", async () => {
    const fixturesPath = defaultFixturesPath();
    const [jobs, events, config] = await Promise.all([loadJobs(fixturesPath), loadEvents(fixturesPath), loadConfig(fixturesPath)]);
    expect(jobs).toHaveLength(20);
    expect(events.length).toBeGreaterThanOrEqual(40);
    expect(config.fixture_mode).toBe(true);
  });

  test("filters jobs", async () => {
    const jobs = await loadJobs(defaultFixturesPath());
    expect(filterJobs(jobs, "failed").every((job) => job.status === "failed")).toBe(true);
    expect(filterJobs(jobs, undefined, "frontend").length).toBeGreaterThan(0);
  });

  test("computes stats", async () => {
    const jobs = await loadJobs(defaultFixturesPath());
    const stats = computeStats(jobs);
    expect(stats.total).toBe(20);
    expect(stats.by_status.running).toBeGreaterThan(0);
  });
});
