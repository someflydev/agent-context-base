package dev.tenantcore.auth.routes;

import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.Tenant;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Collection;
import java.util.Map;

@RestController
@RequestMapping("/admin/tenants")
public class AdminController {

    private final InMemoryStore store;

    public AdminController(InMemoryStore store) {
        this.store = store;
    }

    @GetMapping
    @PreAuthorize("hasAuthority('admin:tenant:create')")
    public ResponseEntity<Collection<Tenant>> listTenants() {
        return ResponseEntity.ok(store.getAllTenants());
    }

    @PostMapping
    @PreAuthorize("hasAuthority('admin:tenant:create')")
    public ResponseEntity<?> createTenant(@RequestBody Map<String, String> body) {
        Tenant tenant = store.createTenant(
            body.getOrDefault("slug", "tenant-" + System.currentTimeMillis()),
            body.getOrDefault("name", "Tenant"),
            body.getOrDefault("first_admin_email", "admin@example.test")
        );
        return ResponseEntity.status(HttpStatus.CREATED).body(tenant);
    }
}
