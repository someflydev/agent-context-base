import React from "react";
import { Box, Text } from "ink";

import type { Job } from "../core/models.js";

interface JobDetailProps {
  job: Job | null;
}

export function JobDetail({ job }: JobDetailProps): React.JSX.Element {
  if (!job) {
    return (
      <Box flexDirection="column" borderStyle="round" width="45%" paddingX={1}>
        <Text>No jobs match the current filter.</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" borderStyle="round" width="45%" paddingX={1}>
      <Text>{job.name}</Text>
      <Text>ID: {job.id}</Text>
      <Text>Status: {job.status}</Text>
      <Text>Started: {job.started_at ?? "-"}</Text>
      <Text>Duration: {job.duration_s ?? "-"}s</Text>
      <Text>Tags: {job.tags.join(", ")}</Text>
      <Text>Output:</Text>
      {job.output_lines.map((line) => (
        <Text key={line}>- {line}</Text>
      ))}
    </Box>
  );
}
