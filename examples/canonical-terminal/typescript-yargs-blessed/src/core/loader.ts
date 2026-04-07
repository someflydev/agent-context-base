import { readFile } from "node:fs/promises";
import path from "node:path";

import type { Config, Event, Job } from "./models.js";

export class FixtureError extends Error {}

export function defaultFixturesPath(): string {
  if (process.env.TASKFLOW_FIXTURES_PATH) {
    return path.resolve(process.env.TASKFLOW_FIXTURES_PATH);
  }
  return path.resolve(import.meta.dirname, "../../../fixtures");
}

async function loadJsonFile<T>(fixturesPath: string, filename: string): Promise<T> {
  const fixtureDir = path.resolve(fixturesPath);
  const target = path.join(fixtureDir, filename);
  try {
    const payload = await readFile(target, "utf8");
    return JSON.parse(payload) as T;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new FixtureError(`failed to load ${target}: ${message}`);
  }
}

export async function loadJobs(fixturesPath: string): Promise<Job[]> {
  return loadJsonFile<Job[]>(fixturesPath, "jobs.json");
}

export async function loadEvents(fixturesPath: string): Promise<Event[]> {
  const events = await loadJsonFile<Event[]>(fixturesPath, "events.json");
  return [...events].sort((left, right) => left.timestamp.localeCompare(right.timestamp));
}

export async function loadConfig(fixturesPath: string): Promise<Config> {
  return loadJsonFile<Config>(fixturesPath, "config.json");
}
