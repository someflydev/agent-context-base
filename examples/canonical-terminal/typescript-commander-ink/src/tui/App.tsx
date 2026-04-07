import React from "react";
import { Box, Text, useApp, useInput } from "ink";
import { render } from "ink";

import type { JobStatus } from "../core/models.js";
import { JobDetail } from "./JobDetail.js";
import { JobTable } from "./JobTable.js";
import { StatsBar } from "./StatsBar.js";
import { useJobs } from "./useJobs.js";

const FILTERS: Array<JobStatus | undefined> = [undefined, "pending", "running", "done", "failed"];

export function TaskFlowApp({ fixturesPath }: { fixturesPath: string }): React.JSX.Element {
  const { exit } = useApp();
  const { filteredJobs, selectedIndex, selectedJob, stats, config, statusFilter, setStatusFilter, moveSelection, refresh } =
    useJobs(fixturesPath);

  useInput((input, key) => {
    if (input === "q") {
      exit();
      return;
    }
    if (input === "r") {
      void refresh();
      return;
    }
    if (input === "f") {
      const currentIndex = FILTERS.findIndex((value) => value === statusFilter);
      setStatusFilter(FILTERS[(currentIndex + 1) % FILTERS.length]);
      return;
    }
    if (key.upArrow) {
      moveSelection(-1);
    }
    if (key.downArrow) {
      moveSelection(1);
    }
  });

  return (
    <Box flexDirection="column">
      <StatsBar stats={stats} config={config} filterLabel={statusFilter ?? "all"} />
      <Box marginTop={1}>
        <JobTable jobs={filteredJobs} selectedIndex={selectedIndex} />
        <JobDetail job={selectedJob} />
      </Box>
      <Text>Keys: q quit | r refresh | f filter | ↑↓ navigate</Text>
    </Box>
  );
}

export function renderApp(fixturesPath: string): void {
  render(<TaskFlowApp fixturesPath={fixturesPath} />);
}
