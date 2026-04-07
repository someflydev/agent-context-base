import type { Job, Stats } from "../core/models.js";

export function markerWrap(begin: string, content: string, end: string): string {
  return [begin, content, end].filter(Boolean).join("\n");
}

export function jobsTable(jobs: Job[]): string {
  const lines = [`${"ID".padEnd(8)} ${"NAME".padEnd(24)} ${"STATUS".padEnd(8)} ${"STARTED_AT".padEnd(20)} TAGS`];
  for (const job of jobs) {
    lines.push(
      `${job.id.padEnd(8)} ${job.name.padEnd(24)} ${job.status.padEnd(8)} ${(job.started_at ?? "-").padEnd(20)} ${job.tags.join(",")}`,
    );
  }
  return lines.join("\n");
}

export function jobPlain(job: Job): string {
  return [
    `ID: ${job.id}`,
    `Name: ${job.name}`,
    `Status: ${job.status}`,
    `Started: ${job.started_at ?? "-"}`,
    `Duration (s): ${job.duration_s ?? "-"}`,
    `Tags: ${job.tags.join(", ")}`,
    "Output:",
    ...job.output_lines.map((line) => `  - ${line}`),
  ].join("\n");
}

export function statsPlain(stats: Stats): string {
  return [
    `Total jobs: ${stats.total}`,
    `Done: ${stats.by_status.done}`,
    `Failed: ${stats.by_status.failed}`,
    `Running: ${stats.by_status.running}`,
    `Pending: ${stats.by_status.pending}`,
    `Average duration (s): ${stats.avg_duration_s ?? "-"}`,
    `Failure rate: ${stats.failure_rate}`,
  ].join("\n");
}
