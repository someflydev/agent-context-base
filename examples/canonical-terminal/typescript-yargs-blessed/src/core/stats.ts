import type { Job, JobStatus, Stats } from "./models.js";

const STATUSES: JobStatus[] = ["pending", "running", "done", "failed"];

export function computeStats(jobs: Job[]): Stats {
  const byStatus = STATUSES.reduce(
    (accumulator, status) => ({ ...accumulator, [status]: 0 }),
    {} as Record<JobStatus, number>,
  );
  const durations: number[] = [];

  for (const job of jobs) {
    byStatus[job.status] += 1;
    if (typeof job.duration_s === "number") {
      durations.push(job.duration_s);
    }
  }

  const avgDuration =
    durations.length > 0
      ? Number((durations.reduce((total, value) => total + value, 0) / durations.length).toFixed(2))
      : null;
  const failureRate = jobs.length > 0 ? Number((byStatus.failed / jobs.length).toFixed(2)) : 0;

  return {
    total: jobs.length,
    by_status: byStatus,
    avg_duration_s: avgDuration,
    failure_rate: failureRate,
  };
}
