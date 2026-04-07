package dev.agentcontext.taskflow.core;

import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

public final class JobFilter {
    private JobFilter() {
    }

    public static List<Job> filterJobs(List<Job> jobs, String status, String tag) {
        return jobs.stream()
            .filter(job -> status == null || job.status().value().equals(status))
            .filter(job -> tag == null || job.tags().contains(tag))
            .sorted(Comparator.comparing(Job::id))
            .collect(Collectors.toList());
    }
}
