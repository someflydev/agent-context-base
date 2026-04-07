import { useEffect, useState } from "react";

import { filterJobs, sortJobs } from "../core/filters.js";
import { loadConfig, loadJobs } from "../core/loader.js";
import { computeStats } from "../core/stats.js";
import type { Config, Job, JobStatus, Stats } from "../core/models.js";

export interface UseJobsState {
  jobs: Job[];
  filteredJobs: Job[];
  selectedIndex: number;
  selectedJob: Job | null;
  stats: Stats;
  config: Config | null;
  statusFilter: JobStatus | undefined;
  setStatusFilter: (value: JobStatus | undefined) => void;
  moveSelection: (delta: number) => void;
  refresh: () => Promise<void>;
}

export function useJobs(fixturesPath: string): UseJobsState {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<Stats>({
    total: 0,
    by_status: { pending: 0, running: 0, done: 0, failed: 0 },
    avg_duration_s: null,
    failure_rate: 0,
  });
  const [config, setConfig] = useState<Config | null>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [statusFilter, setStatusFilter] = useState<JobStatus | undefined>(undefined);

  const filteredJobs = sortJobs(filterJobs(jobs, { status: statusFilter }));
  const selectedJob = filteredJobs[selectedIndex] ?? filteredJobs[0] ?? null;

  async function refresh(): Promise<void> {
    const [loadedJobs, loadedConfig] = await Promise.all([loadJobs(fixturesPath), loadConfig(fixturesPath)]);
    const sortedJobs = sortJobs(loadedJobs);
    setJobs(sortedJobs);
    setStats(computeStats(sortedJobs));
    setConfig(loadedConfig);
    setSelectedIndex((current) => Math.min(current, Math.max(sortJobs(filterJobs(sortedJobs, { status: statusFilter })).length - 1, 0)));
  }

  useEffect(() => {
    void refresh();
  }, [fixturesPath]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [statusFilter]);

  return {
    jobs,
    filteredJobs,
    selectedIndex,
    selectedJob,
    stats,
    config,
    statusFilter,
    setStatusFilter,
    moveSelection(delta) {
      setSelectedIndex((current) => {
        const maxIndex = Math.max(filteredJobs.length - 1, 0);
        return Math.min(Math.max(current + delta, 0), maxIndex);
      });
    },
    refresh,
  };
}
