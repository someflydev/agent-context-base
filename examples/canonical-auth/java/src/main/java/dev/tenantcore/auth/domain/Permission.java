package dev.tenantcore.auth.domain;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;

public record Permission(
    String id,
    String name,
    String description,
    @JsonProperty("created_at") Instant createdAt
) {}
