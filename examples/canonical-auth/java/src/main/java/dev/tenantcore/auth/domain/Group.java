package dev.tenantcore.auth.domain;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;

public record Group(
    String id,
    @JsonProperty("tenant_id") String tenantId,
    String slug,
    String name,
    @JsonProperty("created_at") Instant createdAt
) {}
