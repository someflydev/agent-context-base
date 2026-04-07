package dev.agentcontext.taskflow.core;

import com.fasterxml.jackson.annotation.JsonProperty;

public record Config(
    @JsonProperty("queue_name") String queueName,
    @JsonProperty("refresh_interval_s") int refreshIntervalS,
    @JsonProperty("max_display_jobs") int maxDisplayJobs,
    @JsonProperty("default_output") String defaultOutput,
    @JsonProperty("fixture_mode") boolean fixtureMode
) {
}
