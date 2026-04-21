package dev.tenantcore.auth.domain;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;

public record Tenant(
    String id,
    String slug,
    String name,
    @JsonProperty("created_at") Instant createdAt,
    @JsonProperty("is_active") boolean isActive
) {}
