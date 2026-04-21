package dev.tenantcore.auth.routes;

import dev.tenantcore.auth.auth.AuthContext;
import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.User;
import dev.tenantcore.auth.registry.RouteMetadata;
import dev.tenantcore.auth.registry.RouteRegistry;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.format.DateTimeFormatter;
import java.util.Map;

@RestController
public class MeController {

    private final InMemoryStore store;

    public MeController(InMemoryStore store) {
        this.store = store;
    }

    @GetMapping("/me")
    public ResponseEntity<Map<String, Object>> me() {
        AuthContext auth = (AuthContext) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        User user = store.getUserById(auth.sub());

        String tenantName = null;
        if (auth.tenantId() != null) {
            tenantName = store.getTenantName(auth.tenantId());
        }

        var allowedRoutesMapped = RouteRegistry.getAllowedRoutes(auth).stream()
            .map(this::toRoutePayload)
            .toList();

        Map<String, Object> responseMap = new java.util.LinkedHashMap<>();
        responseMap.put("sub", auth.sub());
        responseMap.put("email", auth.email());
        responseMap.put("display_name", user.displayName());
        responseMap.put("tenant_id", auth.tenantId() != null ? auth.tenantId() : null);
        responseMap.put("tenant_name", tenantName != null ? tenantName : null);
        responseMap.put("tenant_role", auth.tenantRole() != null ? auth.tenantRole() : null);
        responseMap.put("groups", auth.groups());
        responseMap.put("permissions", auth.permissions());
        responseMap.put("acl_ver", auth.aclVer());
        responseMap.put("allowed_routes", allowedRoutesMapped);
        responseMap.put("guide_sections", RouteRegistry.getGuideSections(auth));
        responseMap.put("issued_at", DateTimeFormatter.ISO_INSTANT.format(auth.issuedAt()));
        responseMap.put("expires_at", DateTimeFormatter.ISO_INSTANT.format(auth.expiresAt()));

        return ResponseEntity.ok(responseMap);
    }

    private Map<String, Object> toRoutePayload(RouteMetadata route) {
        return Map.of(
            "method", route.method(),
            "path", route.path(),
            "permission", route.permission() == null ? "" : route.permission(),
            "description", route.description(),
            "service", route.service(),
            "resource", route.resource(),
            "action", route.action()
        );
    }
}
