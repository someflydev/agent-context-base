import type { Job, JobFilterOptions } from "./models.js";

export function filterJobs(jobs: Job[], options: JobFilterOptions = {}): Job[] {
  return jobs.filter((job) => {
    if (options.status && job.status !== options.status) {
      return false;
    }
    if (options.tag && !job.tags.includes(options.tag)) {
      return false;
    }
    return true;
  });
}

export function sortJobs(jobs: Job[]): Job[] {
  return [...jobs].sort((left, right) => left.id.localeCompare(right.id));
}
