package dev.agentcontext.taskflow.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record Job(
    String id,
    String name,
    JobStatus status,
    @JsonProperty("started_at") String startedAt,
    @JsonProperty("duration_s") Double durationS,
    List<String> tags,
    @JsonProperty("output_lines") List<String> outputLines
) {
}
