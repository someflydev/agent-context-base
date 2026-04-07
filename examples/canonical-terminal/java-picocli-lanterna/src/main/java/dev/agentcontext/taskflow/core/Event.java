package dev.agentcontext.taskflow.core;

import com.fasterxml.jackson.annotation.JsonProperty;

public record Event(
    @JsonProperty("event_id") String eventId,
    @JsonProperty("job_id") String jobId,
    @JsonProperty("event_type") String eventType,
    String timestamp,
    String message
) {
}
