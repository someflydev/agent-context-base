package io.agentcontextbase.faker.domain

import com.fasterxml.jackson.annotation.JsonProperty

data class Organization(
    val id: String,
    val name: String,
    val slug: String,
    val plan: String,
    val region: String,
    @JsonProperty("created_at") val createdAt: String,
    @JsonProperty("owner_email") val ownerEmail: String,
)

data class User(
    val id: String,
    val email: String,
    @JsonProperty("full_name") val fullName: String,
    val locale: String,
    val timezone: String,
    @JsonProperty("created_at") val createdAt: String,
)

data class Membership(
    val id: String,
    @JsonProperty("org_id") val orgId: String,
    @JsonProperty("user_id") val userId: String,
    val role: String,
    @JsonProperty("joined_at") val joinedAt: String,
    @JsonProperty("invited_by") val invitedBy: String?,
)

data class Project(
    val id: String,
    @JsonProperty("org_id") val orgId: String,
    val name: String,
    val status: String,
    @JsonProperty("created_by") val createdBy: String,
    @JsonProperty("created_at") val createdAt: String,
)

data class AuditEvent(
    val id: String,
    @JsonProperty("org_id") val orgId: String,
    @JsonProperty("user_id") val userId: String,
    @JsonProperty("project_id") val projectId: String,
    val action: String,
    @JsonProperty("resource_type") val resourceType: String,
    @JsonProperty("resource_id") val resourceId: String,
    val ts: String,
)

data class ApiKey(
    val id: String,
    @JsonProperty("org_id") val orgId: String,
    @JsonProperty("created_by") val createdBy: String,
    val name: String,
    @JsonProperty("key_prefix") val keyPrefix: String,
    @JsonProperty("created_at") val createdAt: String,
    @JsonProperty("last_used_at") val lastUsedAt: String?,
)

data class Invitation(
    val id: String,
    @JsonProperty("org_id") val orgId: String,
    @JsonProperty("invited_email") val invitedEmail: String,
    val role: String,
    @JsonProperty("invited_by") val invitedBy: String,
    @JsonProperty("expires_at") val expiresAt: String,
    @JsonProperty("accepted_at") val acceptedAt: String?,
)

data class TenantCoreDataset(
    val profileName: String,
    val seed: Int,
    val organizations: List<Organization>,
    val users: List<User>,
    val memberships: List<Membership>,
    val projects: List<Project>,
    val auditEvents: List<AuditEvent>,
    val apiKeys: List<ApiKey>,
    val invitations: List<Invitation>,
)
