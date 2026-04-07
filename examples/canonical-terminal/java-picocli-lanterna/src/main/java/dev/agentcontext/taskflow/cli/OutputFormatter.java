package dev.agentcontext.taskflow.cli;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import dev.agentcontext.taskflow.core.Job;
import dev.agentcontext.taskflow.core.Stats;
import java.util.List;

public final class OutputFormatter {
    private static final ObjectMapper MAPPER = new ObjectMapper().findAndRegisterModules();

    private OutputFormatter() {
    }

    public static String markerWrap(String begin, String content, String end) {
        return begin + System.lineSeparator() + content + System.lineSeparator() + end;
    }

    public static String jobsTable(List<Job> jobs) {
        StringBuilder builder = new StringBuilder();
        builder.append(String.format("%-8s %-24s %-8s %-20s %s%n", "ID", "NAME", "STATUS", "STARTED_AT", "TAGS"));
        for (Job job : jobs) {
            builder.append(String.format(
                "%-8s %-24s %-8s %-20s %s%n",
                job.id(),
                job.name(),
                job.status().value(),
                job.startedAt() == null ? "-" : job.startedAt(),
                String.join(",", job.tags())
            ));
        }
        return builder.toString().trim();
    }

    public static String jobPlain(Job job) {
        StringBuilder builder = new StringBuilder();
        builder.append("ID: ").append(job.id()).append(System.lineSeparator());
        builder.append("Name: ").append(job.name()).append(System.lineSeparator());
        builder.append("Status: ").append(job.status().value()).append(System.lineSeparator());
        builder.append("Started: ").append(job.startedAt() == null ? "-" : job.startedAt()).append(System.lineSeparator());
        builder.append("Duration (s): ").append(job.durationS() == null ? "-" : job.durationS()).append(System.lineSeparator());
        builder.append("Tags: ").append(String.join(", ", job.tags())).append(System.lineSeparator());
        builder.append("Output:");
        for (String line : job.outputLines()) {
            builder.append(System.lineSeparator()).append("  - ").append(line);
        }
        return builder.toString();
    }

    public static String statsPlain(Stats stats) {
        return String.join(
            System.lineSeparator(),
            "Total jobs: " + stats.total(),
            "Done: " + stats.byStatus().getOrDefault("done", 0),
            "Failed: " + stats.byStatus().getOrDefault("failed", 0),
            "Running: " + stats.byStatus().getOrDefault("running", 0),
            "Pending: " + stats.byStatus().getOrDefault("pending", 0),
            "Average duration (s): " + (stats.avgDurationS() == null ? "-" : stats.avgDurationS()),
            "Failure rate: " + stats.failureRate()
        );
    }

    public static String json(Object value) {
        try {
            return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
        } catch (JsonProcessingException error) {
            throw new IllegalStateException("failed to serialize json", error);
        }
    }
}
