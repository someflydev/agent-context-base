package dev.agentcontext.taskflow.core;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public record Stats(
    int total,
    @JsonProperty("by_status") Map<String, Integer> byStatus,
    @JsonProperty("avg_duration_s") Double avgDurationS,
    @JsonProperty("failure_rate") double failureRate
) {
}
