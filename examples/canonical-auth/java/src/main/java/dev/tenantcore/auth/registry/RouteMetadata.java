package dev.tenantcore.auth.registry;

import java.util.List;
import java.util.stream.Collectors;

public record RouteMetadata(
    String method,
    String path,
    String permission,
    boolean tenantScoped,
    String description,
    String service,
    String resource,
    String action,
    boolean isPublic,
    boolean superAdminOnly,
    String docsSection
) {}
