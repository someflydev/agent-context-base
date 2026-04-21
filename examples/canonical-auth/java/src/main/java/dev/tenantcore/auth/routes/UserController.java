package dev.tenantcore.auth.routes;

import dev.tenantcore.auth.auth.AuthContext;
import dev.tenantcore.auth.domain.InMemoryStore;
import dev.tenantcore.auth.domain.User;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.Collection;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/users")
public class UserController {

    private final InMemoryStore store;

    public UserController(InMemoryStore store) {
        this.store = store;
    }

    private AuthContext getAuth() {
        return (AuthContext) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
    }

    @GetMapping
    @PreAuthorize("hasAuthority('iam:user:read')")
    public ResponseEntity<Collection<User>> listUsers() {
        return ResponseEntity.ok(store.getAllUsers(getAuth().tenantId()));
    }

    @PostMapping
    @PreAuthorize("hasAuthority('iam:user:invite')")
    public ResponseEntity<?> inviteUser(@RequestBody Map<String, Object> body) {
        User user = store.inviteUser(
            getAuth().tenantId(),
            String.valueOf(body.get("email")),
            String.valueOf(body.getOrDefault("display_name", body.getOrDefault("displayName", "Invited User"))),
            body.get("group_slugs") instanceof List<?> groupSlugs
                ? groupSlugs.stream().filter(String.class::isInstance).map(String.class::cast).toList()
                : List.of()
        );
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('iam:user:read')")
    public ResponseEntity<?> getUser(@PathVariable String id) {
        User user = store.getUserById(id);
        if (user == null || !java.util.Objects.equals(user.tenantId(), getAuth().tenantId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        return ResponseEntity.ok(user);
    }

    @PatchMapping("/{id}")
    @PreAuthorize("hasAuthority('iam:user:update')")
    public ResponseEntity<?> updateUser(@PathVariable String id, @RequestBody Map<String, Object> body) {
        User existing = store.getUserById(id);
        if (existing == null || !java.util.Objects.equals(existing.tenantId(), getAuth().tenantId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        }
        return ResponseEntity.ok(Map.of(
            "id", existing.id(),
            "email", existing.email(),
            "display_name", body.getOrDefault("display_name", existing.displayName())
        ));
    }
}
