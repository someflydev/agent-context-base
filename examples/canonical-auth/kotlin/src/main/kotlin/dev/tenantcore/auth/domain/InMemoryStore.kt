package dev.tenantcore.auth.domain

import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.kotlin.registerKotlinModule
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.util.UUID

class InMemoryStore private constructor(
    private val users: MutableMap<String, User>,
    private val tenants: MutableMap<String, Tenant>,
    private val groups: MutableMap<String, Group>,
    private val permissions: MutableMap<String, Permission>,
    private val memberships: MutableList<Membership>,
    private val groupPermissions: MutableList<GroupPermission>,
    private val userGroups: MutableList<UserGroup>,
) {
    fun getUserById(id: String): User? = users[id]

    fun getUserByEmail(email: String): User? = users.values.firstOrNull { it.email == email }

    fun getActiveMembership(userId: String): Membership? =
        memberships.firstOrNull { it.userId == userId && it.isActive }

    fun verifyMembership(userId: String, tenantId: String): Boolean =
        memberships.any { it.userId == userId && it.tenantId == tenantId && it.isActive }

    fun getTenantName(tenantId: String): String? = tenants[tenantId]?.name

    fun getGroupsForUser(userId: String, tenantId: String): List<Group> =
        userGroups.filter { it.userId == userId }
            .mapNotNull { groups[it.groupId] }
            .filter { it.tenantId == tenantId }

    fun getEffectivePermissions(userId: String): List<String> {
        val membership = getActiveMembership(userId)
        return when (membership?.tenantRole) {
            "tenant_admin" -> permissions.values.map { it.name }.sorted()
            "super_admin" -> getAdminPermissions()
            else -> {
                val groupIds = userGroups.filter { it.userId == userId }.map { it.groupId }.toSet()
                groupPermissions.filter { it.groupId in groupIds }
                    .mapNotNull { permissions[it.permissionId]?.name }
                    .toSet()
                    .sorted()
            }
        }
    }

    fun getAdminPermissions(): List<String> =
        permissions.values.map { it.name }.filter { it.startsWith("admin:") }.sorted()

    fun getAllUsers(tenantId: String): List<User> =
        users.values.filter { it.tenantId == tenantId }.sortedBy { it.email }

    fun getAllGroups(tenantId: String): List<Group> =
        groups.values.filter { it.tenantId == tenantId }.sortedBy { it.slug }

    fun getAllPermissions(): List<Permission> = permissions.values.sortedBy { it.name }

    fun getAllTenants(): List<Tenant> = tenants.values.sortedBy { it.slug }

    fun inviteUser(tenantId: String, email: String, displayName: String, groupSlugs: List<String>): User {
        val user = User(
            id = "u-${UUID.randomUUID()}",
            email = email,
            displayName = displayName,
            tenantId = tenantId,
            createdAt = Instant.now(),
            isActive = true,
            aclVer = 1,
        )
        users[user.id] = user
        memberships += Membership(
            id = "m-${UUID.randomUUID()}",
            userId = user.id,
            tenantId = tenantId,
            tenantRole = "tenant_member",
            createdAt = Instant.now(),
            isActive = true,
        )
        groupSlugs.mapNotNull { slug -> groups.values.firstOrNull { it.slug == slug && it.tenantId == tenantId } }
            .forEach { group ->
                userGroups += UserGroup(
                    id = "ug-${UUID.randomUUID()}",
                    userId = user.id,
                    groupId = group.id,
                    joinedAt = Instant.now(),
                )
            }
        return user
    }

    fun createGroup(tenantId: String, slug: String, name: String): Group {
        val group = Group(
            id = "g-${UUID.randomUUID()}",
            tenantId = tenantId,
            slug = slug,
            name = name,
            createdAt = Instant.now(),
        )
        groups[group.id] = group
        return group
    }

    fun assignPermissionToGroup(groupId: String, permissionName: String, tenantId: String): Boolean {
        val group = groups[groupId] ?: return false
        if (group.tenantId != tenantId) return false
        val permission = permissions.values.firstOrNull { it.name == permissionName } ?: return false
        groupPermissions += GroupPermission(
            id = "gp-${UUID.randomUUID()}",
            groupId = groupId,
            permissionId = permission.id,
            grantedAt = Instant.now(),
        )
        return true
    }

    fun assignUserToGroup(groupId: String, userId: String, tenantId: String): Boolean {
        val group = groups[groupId] ?: return false
        val user = users[userId] ?: return false
        if (group.tenantId != tenantId || user.tenantId != tenantId) return false
        userGroups += UserGroup(
            id = "ug-${UUID.randomUUID()}",
            userId = userId,
            groupId = groupId,
            joinedAt = Instant.now(),
        )
        return true
    }

    fun createTenant(slug: String, name: String, firstAdminEmail: String): Tenant {
        val tenant = Tenant(
            id = "t-${UUID.randomUUID()}",
            slug = slug,
            name = name,
            createdAt = Instant.now(),
            isActive = true,
        )
        tenants[tenant.id] = tenant
        val admin = User(
            id = "u-${UUID.randomUUID()}",
            email = firstAdminEmail,
            displayName = "$name Admin",
            tenantId = tenant.id,
            createdAt = Instant.now(),
            isActive = true,
            aclVer = 1,
        )
        users[admin.id] = admin
        memberships += Membership(
            id = "m-${UUID.randomUUID()}",
            userId = admin.id,
            tenantId = tenant.id,
            tenantRole = "tenant_admin",
            createdAt = Instant.now(),
            isActive = true,
        )
        return tenant
    }

    companion object {
        private val canonicalPermissionNames = listOf(
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
            "admin:audit:read",
        )

        fun loadFromFixtures(fixtureDir: Path): InMemoryStore {
            val mapper = ObjectMapper()
                .registerKotlinModule()
                .registerModule(JavaTimeModule())
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
            val users = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("users.json")), object : TypeReference<List<User>>() {})
            val tenants = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("tenants.json")), object : TypeReference<List<Tenant>>() {})
            val groups = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("groups.json")), object : TypeReference<List<Group>>() {})
            val permissions = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("permissions.json")), object : TypeReference<List<Permission>>() {})
            val memberships = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("memberships.json")), object : TypeReference<List<Membership>>() {})
            val groupPermissions = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("group_permissions.json")), object : TypeReference<List<GroupPermission>>() {})
            val userGroups = mapper.readValue(Files.readAllBytes(fixtureDir.resolve("user_groups.json")), object : TypeReference<List<UserGroup>>() {})

            val store = InMemoryStore(
                users.associateBy { it.id }.toMutableMap(),
                tenants.associateBy { it.id }.toMutableMap(),
                groups.associateBy { it.id }.toMutableMap(),
                permissions.associateBy { it.id }.toMutableMap(),
                memberships.toMutableList(),
                groupPermissions.toMutableList(),
                userGroups.toMutableList(),
            )
            store.seedCanonicalPermissions()
            return store
        }
    }

    private fun seedCanonicalPermissions() {
        val existing = permissions.values.map { it.name }.toSet()
        canonicalPermissionNames.filterNot(existing::contains).forEach { permissionName ->
            val permissionId = "perm-${permissionName.replace(':', '-')}"
            permissions[permissionId] = Permission(
                id = permissionId,
                name = permissionName,
                description = "Canonical seeded permission",
                createdAt = Instant.parse("2025-01-01T00:00:00Z"),
            )
        }
    }
}
