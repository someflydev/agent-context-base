export type JobStatus = "pending" | "running" | "done" | "failed";

export interface Job {
  id: string;
  name: string;
  status: JobStatus;
  started_at: string | null;
  duration_s: number | null;
  tags: string[];
  output_lines: string[];
}

export interface Event {
  event_id: string;
  job_id: string;
  event_type: string;
  timestamp: string;
  message: string;
}

export interface Config {
  queue_name: string;
  refresh_interval_s: number;
  max_display_jobs: number;
  default_output: string;
  fixture_mode: boolean;
}

export interface Stats {
  total: number;
  by_status: Record<JobStatus, number>;
  avg_duration_s: number | null;
  failure_rate: number;
}

export interface JobFilterOptions {
  status?: JobStatus;
  tag?: string;
}
