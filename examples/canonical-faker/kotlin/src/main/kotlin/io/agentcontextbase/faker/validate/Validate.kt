package io.agentcontextbase.faker.validate

import io.agentcontextbase.faker.domain.TenantCoreDataset
import io.agentcontextbase.faker.pools.IdPools
import java.time.Instant
import java.time.temporal.ChronoUnit

data class ValidationReport(
    val ok: Boolean,
    val violations: List<String>,
    val counts: Map<String, Int>,
    val seed: Int,
    val profileName: String,
)

fun validate(dataset: TenantCoreDataset): ValidationReport {
    val violations = mutableListOf<String>()
    val counts = mapOf(
        "organizations" to dataset.organizations.size,
        "users" to dataset.users.size,
        "memberships" to dataset.memberships.size,
        "projects" to dataset.projects.size,
        "audit_events" to dataset.auditEvents.size,
        "api_keys" to dataset.apiKeys.size,
        "invitations" to dataset.invitations.size,
    )

    val orgs = mutableMapOf<String, io.agentcontextbase.faker.domain.Organization>()
    dataset.organizations.forEach { org ->
        if (orgs.put(org.id, org) != null) violations += "duplicate organizations.id: ${org.id}"
    }
    val users = mutableMapOf<String, io.agentcontextbase.faker.domain.User>()
    val seenEmails = mutableSetOf<String>()
    dataset.users.forEach { user ->
        users[user.id] = user
        if (!seenEmails.add(user.email.lowercase())) violations += "duplicate users.email: ${user.email}"
    }

    val membershipIds = mutableSetOf<String>()
    dataset.memberships.forEach { membership ->
        membershipIds += membership.id
        val org = orgs[membership.orgId]
        if (org == null) {
            violations += "membership missing org: ${membership.id}"
            return@forEach
        }
        if (users[membership.userId] == null) {
            violations += "membership missing user: ${membership.id}"
            return@forEach
        }
        if (Instant.parse(membership.joinedAt).isBefore(Instant.parse(org.createdAt))) {
            violations += "Rule A violated by membership ${membership.id}"
        }
        if (membership.invitedBy != null && users[membership.invitedBy] == null) {
            violations += "membership invited_by missing user: ${membership.id}"
        }
    }

    val projects = dataset.projects.associateBy { it.id }
    dataset.projects.forEach { project ->
        val org = orgs[project.orgId]
        if (org == null) {
            violations += "project missing org: ${project.id}"
            return@forEach
        }
        if (Instant.parse(project.createdAt).isBefore(Instant.parse(org.createdAt))) {
            violations += "Rule B violated by project ${project.id}"
        }
    }

    val graph = IdPools.graph(dataset)
    val apiKeyIds = mutableSetOf<String>()
    val keyPrefixes = mutableSetOf<String>()
    dataset.apiKeys.forEach { apiKey ->
        apiKeyIds += apiKey.id
        if (!graph.orgMemberMap[apiKey.orgId].orEmpty().contains(apiKey.createdBy)) {
            violations += "Rule G violated by api_key ${apiKey.id}"
        }
        if (!keyPrefixes.add(apiKey.keyPrefix)) {
            violations += "duplicate api_key.key_prefix: ${apiKey.keyPrefix}"
        }
        if (apiKey.lastUsedAt != null && Instant.parse(apiKey.lastUsedAt).isBefore(Instant.parse(apiKey.createdAt))) {
            violations += "api_key last_used_at before created_at: ${apiKey.id}"
        }
    }

    val invitationIds = mutableSetOf<String>()
    dataset.invitations.forEach { invitation ->
        invitationIds += invitation.id
        if (!graph.orgMemberMap[invitation.orgId].orEmpty().contains(invitation.invitedBy)) {
            violations += "Rule H violated by invitation ${invitation.id}"
        }
        val matchesMember = graph.orgMemberMap[invitation.orgId].orEmpty()
            .mapNotNull { graph.userEmailById[it] }
            .any { it.equals(invitation.invitedEmail, ignoreCase = true) }
        if (matchesMember) {
            violations += "Rule I violated by invitation ${invitation.id}"
        }
        val expiresAt = Instant.parse(invitation.expiresAt)
        if (!expiresAt.isAfter(IdPools.BASE_TIME)) {
            violations += "invitation expiry must be in the future: ${invitation.id}"
        }
        if (expiresAt.isAfter(IdPools.BASE_TIME.plus(30, ChronoUnit.DAYS))) {
            violations += "invitation expiry must be within 30 days: ${invitation.id}"
        }
        if (invitation.acceptedAt != null && Instant.parse(invitation.acceptedAt).isAfter(IdPools.BASE_TIME)) {
            violations += "invitation accepted_at must be in the past: ${invitation.id}"
        }
    }

    dataset.projects.forEach { project ->
        if (!graph.orgMemberMap[project.orgId].orEmpty().contains(project.createdBy)) {
            violations += "Rule C violated by project ${project.id}"
        }
    }

    dataset.auditEvents.forEach { event ->
        val project = projects[event.projectId]
        if (project == null) {
            violations += "audit_event missing project: ${event.id}"
            return@forEach
        }
        if (!graph.orgMemberMap[event.orgId].orEmpty().contains(event.userId)) {
            violations += "Rule D violated by audit_event ${event.id}"
        }
        if (project.orgId != event.orgId) {
            violations += "Rule E violated by audit_event ${event.id}"
        }
        if (Instant.parse(event.ts).isBefore(Instant.parse(project.createdAt))) {
            violations += "Rule F violated by audit_event ${event.id}"
        }
        val membership = graph.membershipByOrgUser["${event.orgId}:${event.userId}"]
        if (membership != null && Instant.parse(event.ts).isBefore(Instant.parse(membership.joinedAt))) {
            violations += "audit event before membership joined_at: ${event.id}"
        }
        when (event.resourceType) {
            "project" -> if (!projects.containsKey(event.resourceId)) violations += "audit event resource project missing: ${event.id}"
            "user" -> if (!users.containsKey(event.resourceId)) violations += "audit event resource user missing: ${event.id}"
            "membership" -> if (!membershipIds.contains(event.resourceId)) violations += "audit event resource membership missing: ${event.id}"
            "api_key" -> if (!apiKeyIds.contains(event.resourceId)) violations += "audit event resource api_key missing: ${event.id}"
            "invitation" -> if (!invitationIds.contains(event.resourceId)) violations += "audit event resource invitation missing: ${event.id}"
        }
    }

    return ValidationReport(
        ok = violations.isEmpty(),
        violations = violations,
        counts = counts,
        seed = dataset.seed,
        profileName = dataset.profileName,
    )
}
