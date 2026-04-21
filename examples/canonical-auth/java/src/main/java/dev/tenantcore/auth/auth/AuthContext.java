package dev.tenantcore.auth.auth;

import java.time.Instant;
import java.util.List;

public record AuthContext(
    String sub,
    String email,
    String tenantId,
    String tenantRole,
    List<String> groups,
    List<String> permissions,
    int aclVer,
    Instant issuedAt,
    Instant expiresAt
) {
    public boolean hasPermission(String permission) {
        return permissions.contains(permission);
    }
}
