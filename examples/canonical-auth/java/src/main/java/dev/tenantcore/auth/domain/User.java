package dev.tenantcore.auth.domain;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;

public record User(
    String id,
    String email,
    @JsonProperty("display_name") String displayName,
    @JsonProperty("tenant_id") String tenantId,
    @JsonProperty("created_at") Instant createdAt,
    @JsonProperty("is_active") boolean isActive,
    @JsonProperty("acl_ver") int aclVer
) {}
