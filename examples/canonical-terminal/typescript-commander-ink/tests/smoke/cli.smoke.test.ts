import path from "node:path";

import { execa } from "execa";
import { beforeAll, describe, expect, test } from "vitest";

const projectRoot = path.resolve(import.meta.dirname, "../..");
const fixturesPath = path.resolve(projectRoot, "../fixtures");
const cliPath = path.resolve(projectRoot, "dist/cli/index.js");

async function runCli(args: string[], reject = true) {
  return execa("node", [cliPath, "--fixtures-path", fixturesPath, ...args], {
    cwd: projectRoot,
    reject,
    env: { ...process.env, TERM: "dumb" },
  });
}

describe("commander smoke", () => {
  beforeAll(async () => {
    await execa("npm", ["run", "build"], { cwd: projectRoot });
  }, 120000);

  test("list_table", async () => {
    const result = await runCli(["list"]);
    expect(result.stdout).toContain("## BEGIN_JOBS ##");
  });

  test("list_json", async () => {
    const result = await runCli(["list", "--output", "json"]);
    const payload = JSON.parse(result.stdout) as Array<Record<string, unknown>>;
    expect(payload).toHaveLength(20);
  });

  test("filter_status", async () => {
    const result = await runCli(["list", "--status", "done", "--output", "json"]);
    const payload = JSON.parse(result.stdout) as Array<Record<string, unknown>>;
    expect(payload.length).toBeGreaterThan(0);
    expect(payload.every((job) => job.status === "done")).toBe(true);
  });

  test("inspect_job", async () => {
    const result = await runCli(["inspect", "job-001", "--output", "json"]);
    const payload = JSON.parse(result.stdout) as Record<string, unknown>;
    expect(payload.id).toBe("job-001");
  });

  test("stats_json", async () => {
    const result = await runCli(["stats", "--output", "json"]);
    const payload = JSON.parse(result.stdout) as Record<string, unknown>;
    expect(payload.total).toBe(20);
  });

  test("watch_no_tui", async () => {
    const result = await runCli(["watch", "--no-tui"]);
    expect(result.stdout).toContain("## BEGIN_JOBS ##");
  });

  test("missing_fixtures", async () => {
    const result = await execa(
      "node",
      [cliPath, "--fixtures-path", path.join(fixturesPath, "missing"), "list"],
      { cwd: projectRoot, reject: false, env: { ...process.env, TERM: "dumb" } },
    );
    expect(result.exitCode).not.toBe(0);
  });
});
