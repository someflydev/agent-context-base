package dev.tenantcore.auth.domain;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import org.springframework.stereotype.Repository;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
public class InMemoryStore {
    private static final List<String> CANONICAL_PERMISSION_NAMES = List.of(
        "iam:user:read",
        "iam:user:create",
        "iam:user:update",
        "iam:user:delete",
        "iam:user:invite",
        "iam:group:read",
        "iam:group:create",
        "iam:group:update",
        "iam:group:delete",
        "iam:group:assign_permission",
        "iam:group:assign_user",
        "iam:tenant:read",
        "iam:tenant:create",
        "iam:tenant:update",
        "iam:permission:read",
        "billing:invoice:read",
        "billing:invoice:create",
        "billing:subscription:read",
        "billing:subscription:update",
        "reports:usage:read",
        "reports:usage:export",
        "reports:audit:read",
        "admin:tenant:create",
        "admin:tenant:suspend",
        "admin:audit:read"
    );

    private final Map<String, User> users = new HashMap<>();
    private final Map<String, Tenant> tenants = new HashMap<>();
    private final Map<String, Group> groups = new HashMap<>();
    private final Map<String, Permission> permissions = new HashMap<>();

    private final List<Membership> memberships = new ArrayList<>();
    private final List<GroupPermission> groupPermissions = new ArrayList<>();
    private final List<UserGroup> userGroups = new ArrayList<>();

    public record Membership(
        String id,
        @JsonProperty("user_id") String userId,
        @JsonProperty("tenant_id") String tenantId,
        @JsonProperty("tenant_role") String tenantRole,
        @JsonProperty("created_at") Instant createdAt,
        @JsonProperty("is_active") boolean isActive
    ) {}

    public record GroupPermission(
        String id,
        @JsonProperty("group_id") String groupId,
        @JsonProperty("permission_id") String permissionId,
        @JsonProperty("granted_at") Instant grantedAt
    ) {}

    public record UserGroup(
        String id,
        @JsonProperty("user_id") String userId,
        @JsonProperty("group_id") String groupId,
        @JsonProperty("joined_at") Instant joinedAt
    ) {}

    public static InMemoryStore loadFromFixtures(Path fixtureDir) throws IOException {
        ObjectMapper mapper = new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

        InMemoryStore store = new InMemoryStore();

        List<User> userList = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("users.json")), new TypeReference<>() {});
        userList.forEach(u -> store.users.put(u.id(), u));

        List<Tenant> tenantList = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("tenants.json")), new TypeReference<>() {});
        tenantList.forEach(t -> store.tenants.put(t.id(), t));

        List<Group> groupList = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("groups.json")), new TypeReference<>() {});
        groupList.forEach(g -> store.groups.put(g.id(), g));

        List<Permission> permList = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("permissions.json")), new TypeReference<>() {});
        permList.forEach(p -> store.permissions.put(p.id(), p));
        store.seedCanonicalPermissions();

        List<Membership> memList = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("memberships.json")), new TypeReference<>() {});
        store.memberships.addAll(memList);

        List<GroupPermission> gpList = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("group_permissions.json")), new TypeReference<>() {});
        store.groupPermissions.addAll(gpList);

        List<UserGroup> ugList = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("user_groups.json")), new TypeReference<>() {});
        store.userGroups.addAll(ugList);

        return store;
    }

    public User getUserById(String id) {
        return users.get(id);
    }

    public User getUserByEmail(String email) {
        return users.values().stream().filter(u -> u.email().equals(email)).findFirst().orElse(null);
    }

    public Optional<Membership> getActiveMembership(String userId) {
        return memberships.stream()
            .filter(m -> m.userId().equals(userId) && m.isActive())
            .findFirst();
    }

    public Tenant getTenantById(String id) {
        return tenants.get(id);
    }

    public String getTenantName(String id) {
        Tenant t = tenants.get(id);
        return t != null ? t.name() : null;
    }

    public List<Group> getGroupsForUser(String userId, String tenantId) {
        return userGroups.stream()
            .filter(ug -> ug.userId().equals(userId))
            .map(ug -> groups.get(ug.groupId()))
            .filter(Objects::nonNull)
            .filter(g -> tenantId == null || tenantId.equals(g.tenantId()))
            .collect(Collectors.toList());
    }

    public List<String> getEffectivePermissions(String userId) {
        Optional<Membership> membership = getActiveMembership(userId);
        if (membership.isPresent()) {
            String tenantRole = membership.get().tenantRole();
            if ("tenant_admin".equals(tenantRole)) {
                return permissions.values().stream()
                    .map(Permission::name)
                    .sorted()
                    .toList();
            }
            if ("super_admin".equals(tenantRole)) {
                return getAdminPermissions();
            }
        }

        Set<String> perms = new HashSet<>();
        for (UserGroup ug : userGroups) {
            if (ug.userId().equals(userId)) {
                for (GroupPermission gp : groupPermissions) {
                    if (gp.groupId().equals(ug.groupId())) {
                        Permission p = permissions.get(gp.permissionId());
                        if (p != null) {
                            perms.add(p.name());
                        }
                    }
                }
            }
        }
        return perms.stream().sorted().toList();
    }

    public boolean verifyMembership(String userId, String tenantId) {
        return memberships.stream()
            .anyMatch(m -> m.userId().equals(userId) && Objects.equals(m.tenantId(), tenantId) && m.isActive());
    }

    public String getMembershipRole(String userId, String tenantId) {
        return memberships.stream()
            .filter(m -> m.userId().equals(userId) && Objects.equals(m.tenantId(), tenantId) && m.isActive())
            .map(Membership::tenantRole)
            .findFirst()
            .orElse(null);
    }

    public List<String> getAdminPermissions() {
        return permissions.values().stream()
            .map(Permission::name)
            .filter(name -> name.startsWith("admin:"))
            .sorted()
            .toList();
    }

    public Collection<Permission> getAllPermissions() {
        return permissions.values().stream()
            .sorted(Comparator.comparing(Permission::name))
            .toList();
    }

    public Collection<User> getAllUsers(String tenantId) {
        return users.values().stream()
            .filter(u -> tenantId == null || Objects.equals(u.tenantId(), tenantId))
            .collect(Collectors.toList());
    }

    public Collection<Tenant> getAllTenants() {
        return tenants.values().stream()
            .sorted(Comparator.comparing(Tenant::slug))
            .toList();
    }

    public Collection<Group> getAllGroups(String tenantId) {
        return groups.values().stream()
            .filter(g -> tenantId == null || Objects.equals(g.tenantId(), tenantId))
            .collect(Collectors.toList());
    }

    public User inviteUser(String tenantId, String email, String displayName, List<String> groupSlugs) {
        User user = new User(
            "u-" + UUID.randomUUID(),
            email,
            displayName,
            tenantId,
            Instant.now(),
            true,
            1
        );
        users.put(user.id(), user);
        memberships.add(new Membership(
            "m-" + UUID.randomUUID(),
            user.id(),
            tenantId,
            "tenant_member",
            Instant.now(),
            true
        ));
        if (groupSlugs != null) {
            groupSlugs.stream()
                .map(this::findGroupBySlug)
                .filter(Objects::nonNull)
                .filter(group -> tenantId.equals(group.tenantId()))
                .forEach(group -> userGroups.add(new UserGroup(
                    "ug-" + UUID.randomUUID(),
                    user.id(),
                    group.id(),
                    Instant.now()
                )));
        }
        return user;
    }

    public Group createGroup(String tenantId, String slug, String name) {
        Group group = new Group(
            "g-" + UUID.randomUUID(),
            tenantId,
            slug,
            name,
            Instant.now()
        );
        groups.put(group.id(), group);
        return group;
    }

    public boolean assignPermissionToGroup(String groupId, String permissionName, String tenantId) {
        Group group = groups.get(groupId);
        if (group == null || !Objects.equals(group.tenantId(), tenantId)) {
            return false;
        }
        Permission permission = permissions.values().stream()
            .filter(value -> value.name().equals(permissionName))
            .findFirst()
            .orElse(null);
        if (permission == null) {
            return false;
        }
        groupPermissions.add(new GroupPermission(
            "gp-" + UUID.randomUUID(),
            groupId,
            permission.id(),
            Instant.now()
        ));
        return true;
    }

    public boolean assignUserToGroup(String groupId, String userId, String tenantId) {
        Group group = groups.get(groupId);
        User user = users.get(userId);
        if (group == null || user == null) {
            return false;
        }
        if (!Objects.equals(group.tenantId(), tenantId) || !Objects.equals(user.tenantId(), tenantId)) {
            return false;
        }
        userGroups.add(new UserGroup(
            "ug-" + UUID.randomUUID(),
            userId,
            groupId,
            Instant.now()
        ));
        return true;
    }

    public Tenant createTenant(String slug, String name, String firstAdminEmail) {
        String tenantId = "t-" + UUID.randomUUID();
        Tenant tenant = new Tenant(tenantId, slug, name, Instant.now(), true);
        tenants.put(tenant.id(), tenant);
        User admin = new User(
            "u-" + UUID.randomUUID(),
            firstAdminEmail,
            name + " Admin",
            tenant.id(),
            Instant.now(),
            true,
            1
        );
        users.put(admin.id(), admin);
        memberships.add(new Membership(
            "m-" + UUID.randomUUID(),
            admin.id(),
            tenant.id(),
            "tenant_admin",
            Instant.now(),
            true
        ));
        return tenant;
    }

    private Group findGroupBySlug(String slug) {
        return groups.values().stream()
            .filter(group -> group.slug().equals(slug))
            .findFirst()
            .orElse(null);
    }

    private void seedCanonicalPermissions() {
        Set<String> existingNames = permissions.values().stream()
            .map(Permission::name)
            .collect(Collectors.toSet());
        for (String permissionName : CANONICAL_PERMISSION_NAMES) {
            if (existingNames.contains(permissionName)) {
                continue;
            }
            String permissionId = "perm-" + permissionName.replace(':', '-');
            permissions.put(
                permissionId,
                new Permission(
                    permissionId,
                    permissionName,
                    "Canonical seeded permission",
                    Instant.parse("2025-01-01T00:00:00Z")
                )
            );
        }
    }
}
