package dev.tenantcore.auth.domain

import com.fasterxml.jackson.annotation.JsonProperty
import java.time.Instant

data class User(
    val id: String,
    val email: String,
    @JsonProperty("display_name") val displayName: String,
    @JsonProperty("tenant_id") val tenantId: String?,
    @JsonProperty("created_at") val createdAt: Instant,
    @JsonProperty("is_active") val isActive: Boolean,
    @JsonProperty("acl_ver") val aclVer: Int,
)

data class Tenant(
    val id: String,
    val slug: String,
    val name: String,
    @JsonProperty("created_at") val createdAt: Instant,
    @JsonProperty("is_active") val isActive: Boolean,
)

data class Group(
    val id: String,
    @JsonProperty("tenant_id") val tenantId: String,
    val slug: String,
    val name: String,
    @JsonProperty("created_at") val createdAt: Instant,
)

data class Permission(
    val id: String,
    val name: String,
    val description: String,
    @JsonProperty("created_at") val createdAt: Instant,
)

data class Membership(
    val id: String,
    @JsonProperty("user_id") val userId: String,
    @JsonProperty("tenant_id") val tenantId: String?,
    @JsonProperty("tenant_role") val tenantRole: String,
    @JsonProperty("created_at") val createdAt: Instant,
    @JsonProperty("is_active") val isActive: Boolean,
)

data class GroupPermission(
    val id: String,
    @JsonProperty("group_id") val groupId: String,
    @JsonProperty("permission_id") val permissionId: String,
    @JsonProperty("granted_at") val grantedAt: Instant,
)

data class UserGroup(
    val id: String,
    @JsonProperty("user_id") val userId: String,
    @JsonProperty("group_id") val groupId: String,
    @JsonProperty("joined_at") val joinedAt: Instant,
)
