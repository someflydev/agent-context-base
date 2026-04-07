import React from "react";
import { Box, Text } from "ink";

import type { Config, Stats } from "../core/models.js";

interface StatsBarProps {
  stats: Stats;
  config: Config | null;
  filterLabel: string;
}

export function StatsBar({ stats, config, filterLabel }: StatsBarProps): React.JSX.Element {
  return (
    <Box borderStyle="round" paddingX={1} justifyContent="space-between">
      <Text>
        Queue {config?.queue_name ?? "taskflow"} | total {stats.total} | done {stats.by_status.done} | failed{" "}
        {stats.by_status.failed} | running {stats.by_status.running} | pending {stats.by_status.pending}
      </Text>
      <Text>filter {filterLabel}</Text>
    </Box>
  );
}
