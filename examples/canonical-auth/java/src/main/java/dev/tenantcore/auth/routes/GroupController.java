package dev.tenantcore.auth.routes;

import dev.tenantcore.auth.auth.AuthContext;
import dev.tenantcore.auth.domain.Group;
import dev.tenantcore.auth.domain.InMemoryStore;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.Collection;
import java.util.Map;

@RestController
@RequestMapping("/groups")
public class GroupController {

    private final InMemoryStore store;

    public GroupController(InMemoryStore store) {
        this.store = store;
    }

    private AuthContext getAuth() {
        return (AuthContext) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }

    @GetMapping
    @PreAuthorize("hasAuthority('iam:group:read')")
    public ResponseEntity<Collection<Group>> listGroups() {
        return ResponseEntity.ok(store.getAllGroups(getAuth().tenantId()));
    }

    @PostMapping
    @PreAuthorize("hasAuthority('iam:group:create')")
    public ResponseEntity<?> createGroup(@RequestBody Group group) {
        Group created = store.createGroup(getAuth().tenantId(), group.slug(), group.name());
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PostMapping("/{id}/permissions")
    @PreAuthorize("hasAuthority('iam:group:assign_permission')")
    public ResponseEntity<?> assignPermission(@PathVariable String id, @RequestBody Map<String, String> body) {
        boolean assigned = store.assignPermissionToGroup(id, body.get("permission"), getAuth().tenantId());
        if (!assigned) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
        return ResponseEntity.ok().build();
    }

    @PostMapping("/{id}/users")
    @PreAuthorize("hasAuthority('iam:group:assign_user')")
    public ResponseEntity<?> assignUser(@PathVariable String id, @RequestBody Map<String, String> body) {
        boolean assigned = store.assignUserToGroup(id, body.get("user_id"), getAuth().tenantId());
        if (!assigned) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
        return ResponseEntity.ok().build();
    }
}
