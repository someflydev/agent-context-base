package dev.agentcontext.taskflow.core;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class StatsComputer {
    private StatsComputer() {
    }

    public static Stats computeStats(List<Job> jobs) {
        Map<String, Integer> byStatus = new LinkedHashMap<>();
        byStatus.put("pending", 0);
        byStatus.put("running", 0);
        byStatus.put("done", 0);
        byStatus.put("failed", 0);

        double durationTotal = 0;
        int durationCount = 0;
        for (Job job : jobs) {
            byStatus.compute(job.status().value(), (key, value) -> value == null ? 1 : value + 1);
            if (job.durationS() != null) {
                durationTotal += job.durationS();
                durationCount += 1;
            }
        }
        Double avgDuration = durationCount == 0 ? null : Math.round((durationTotal / durationCount) * 100.0) / 100.0;
        double failureRate = jobs.isEmpty() ? 0.0 : Math.round((byStatus.get("failed") / (double) jobs.size()) * 100.0) / 100.0;
        return new Stats(jobs.size(), byStatus, avgDuration, failureRate);
    }
}
