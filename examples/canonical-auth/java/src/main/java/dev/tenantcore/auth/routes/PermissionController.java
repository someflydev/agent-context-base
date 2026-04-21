package dev.tenantcore.auth.routes;

import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.Permission;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Collection;

@RestController
public class PermissionController {

    private final InMemoryStore store;

    public PermissionController(InMemoryStore store) {
        this.store = store;
    }

    @GetMapping("/permissions")
    @PreAuthorize("hasAuthority('iam:permission:read')")
    public ResponseEntity<Collection<Permission>> listPermissions() {
        return ResponseEntity.ok(store.getAllPermissions());
    }
}
