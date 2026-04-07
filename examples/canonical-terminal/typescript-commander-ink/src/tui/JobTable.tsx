import React from "react";
import { Box, Text } from "ink";

import type { Job } from "../core/models.js";

const COLORS: Record<Job["status"], string> = {
  done: "green",
  failed: "red",
  running: "yellow",
  pending: "gray",
};

interface JobTableProps {
  jobs: Job[];
  selectedIndex: number;
}

export function JobTable({ jobs, selectedIndex }: JobTableProps): React.JSX.Element {
  return (
    <Box flexDirection="column" borderStyle="round" width="55%" paddingX={1}>
      <Text>Jobs</Text>
      {jobs.map((job, index) => {
        const isSelected = index === selectedIndex;
        return (
          <Text key={job.id} color={COLORS[job.status]} inverse={isSelected}>
            {job.id.padEnd(8)} {job.name.padEnd(22)} {job.status.padEnd(8)} {job.tags.join(",")}
          </Text>
        );
      })}
    </Box>
  );
}
