import type { Job, JobStatus } from "./models.js";

export function filterJobs(jobs: Job[], status?: JobStatus, tag?: string): Job[] {
  return jobs.filter((job) => {
    if (status && job.status !== status) {
      return false;
    }
    if (tag && !job.tags.includes(tag)) {
      return false;
    }
    return true;
  });
}

export function sortJobs(jobs: Job[]): Job[] {
  return [...jobs].sort((left, right) => left.id.localeCompare(right.id));
}
