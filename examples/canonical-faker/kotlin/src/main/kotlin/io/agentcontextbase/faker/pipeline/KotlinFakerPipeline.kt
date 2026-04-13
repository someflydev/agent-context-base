package io.agentcontextbase.faker.pipeline

import io.agentcontextbase.faker.distributions.Distributions
import io.agentcontextbase.faker.domain.ApiKey
import io.agentcontextbase.faker.domain.AuditEvent
import io.agentcontextbase.faker.domain.Invitation
import io.agentcontextbase.faker.domain.Membership
import io.agentcontextbase.faker.domain.Organization
import io.agentcontextbase.faker.domain.Project
import io.agentcontextbase.faker.domain.TenantCoreDataset
import io.agentcontextbase.faker.domain.User
import io.agentcontextbase.faker.pools.IdPools
import io.agentcontextbase.faker.profiles.Profile
import kotlin.random.Random

private val EDGE_CASE_NAMES = listOf(
    "Sofie D'Aubigne",
    "Bjorn Asmussen",
    "Francois L'Ecuyer",
    "Marta Nunez de la Pena",
    "Zoe Kruger-Renaud",
)
private const val KEY_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"

object KotlinFakerPipeline {
    fun generate(profile: Profile): TenantCoreDataset {
        val random = Random(profile.seed)
        val organizations = mutableListOf<Organization>()
        val users = mutableListOf<User>()
        val memberships = mutableListOf<Membership>()
        val projects = mutableListOf<Project>()
        val apiKeys = mutableListOf<ApiKey>()
        val invitations = mutableListOf<Invitation>()
        val auditEvents = mutableListOf<AuditEvent>()

        val orgSlugs = mutableSetOf<String>()
        val orgEmails = mutableSetOf<String>()
        val userEmails = mutableSetOf<String>()
        val keyPrefixes = mutableSetOf<String>()
        val orgMemberMap = mutableMapOf<String, List<String>>()

        kotlinFakerAvailabilityNote()

        repeat(profile.numOrgs) { index ->
            val baseName = "TenantCore Org ${index + 1}"
            val baseSlug = IdPools.slugify(baseName)
            var slug = baseSlug
            var suffix = 2
            while (!orgSlugs.add(slug)) {
                slug = "$baseSlug-${suffix++}"
            }
            val ownerEmail = uniqueEmail(orgEmails, "owner${index + 1}", "tenantcore-example.test", random)
            organizations += Organization(
                id = IdPools.deterministicId(random),
                name = baseName,
                slug = slug,
                plan = Distributions.weightedPlan(random),
                region = Distributions.weightedRegion(random),
                createdAt = IdPools.boundedPast(random).toString(),
                ownerEmail = ownerEmail,
            )
        }

        repeat(profile.numUsers) { index ->
            val locale = Distributions.weightedLocale(random)
            val edgeCase = random.nextDouble() < 0.05
            val localHint = if (edgeCase) "edgecase$index" else "user${index + 1}"
            users += User(
                id = IdPools.deterministicId(random),
                email = uniqueEmail(userEmails, localHint, "${locale.lowercase().replace("-", "")}.tenantcore-example.test", random),
                fullName = if (edgeCase) EDGE_CASE_NAMES[index % EDGE_CASE_NAMES.size] else "Tenant User ${index + 1}",
                locale = locale,
                timezone = if (edgeCase) "UTC" else IdPools.TIMEZONE_BY_LOCALE.getValue(locale),
                createdAt = IdPools.boundedPast(random).toString(),
            )
        }

        organizations.forEach { organization ->
            val sampled = users.shuffled(random).take(Distributions.memberCount(random, users.size))
            val memberIds = mutableListOf<String>()
            sampled.forEachIndexed { position, user ->
                memberships += Membership(
                    id = IdPools.deterministicId(random),
                    orgId = organization.id,
                    userId = user.id,
                    role = if (position == 0) "owner" else Distributions.weightedMembershipRole(random),
                    joinedAt = IdPools.between(random, java.time.Instant.parse(organization.createdAt), IdPools.BASE_TIME).toString(),
                    invitedBy = if (position == 0) null else memberIds.random(random),
                )
                memberIds += user.id
            }
            orgMemberMap[organization.id] = memberIds
        }

        organizations.forEach { organization ->
            val memberIds = orgMemberMap.getValue(organization.id)
            repeat(Distributions.projectCount(random)) { index ->
                projects += Project(
                    id = IdPools.deterministicId(random),
                    orgId = organization.id,
                    name = "Project ${index + 1} ${organization.slug}",
                    status = Distributions.weightedProjectStatus(random),
                    createdBy = memberIds.random(random),
                    createdAt = IdPools.between(random, java.time.Instant.parse(organization.createdAt), IdPools.BASE_TIME).toString(),
                )
            }
        }

        val projectGraph = IdPools.graph(
            TenantCoreDataset(profile.name, profile.seed, organizations, users, memberships, projects, auditEvents, apiKeys, invitations)
        )

        organizations.forEach { organization ->
            val memberIds = orgMemberMap.getValue(organization.id)
            val memberEmails = memberIds.mapNotNull { projectGraph.userEmailById[it] }.toSet()
            repeat(Distributions.apiKeyCount(random)) {
                var prefix = "tc_${randomKey(random)}"
                while (!keyPrefixes.add(prefix)) {
                    prefix = "tc_${randomKey(random)}"
                }
                val createdAt = IdPools.between(random, java.time.Instant.parse(organization.createdAt), IdPools.BASE_TIME)
                apiKeys += ApiKey(
                    id = IdPools.deterministicId(random),
                    orgId = organization.id,
                    createdBy = memberIds.random(random),
                    name = "token-${organization.slug}",
                    keyPrefix = prefix,
                    createdAt = createdAt.toString(),
                    lastUsedAt = if (random.nextDouble() < 0.7) IdPools.between(random, createdAt, IdPools.BASE_TIME).toString() else null,
                )
            }
            repeat(Distributions.invitationCount(random)) { index ->
                var invitedEmail = "invite-${organization.slug}-$index@tenantcore-example.test"
                while (invitedEmail.lowercase() in memberEmails) {
                    invitedEmail = "invite-${organization.slug}-$index-${random.nextInt(1, 999)}@tenantcore-example.test"
                }
                invitations += Invitation(
                    id = IdPools.deterministicId(random),
                    orgId = organization.id,
                    invitedEmail = invitedEmail,
                    role = Distributions.weightedInvitationRole(random),
                    invitedBy = memberIds.random(random),
                    expiresAt = IdPools.BASE_TIME.plus(random.nextInt(1, 31).toLong(), java.time.temporal.ChronoUnit.DAYS).toString(),
                    acceptedAt = if (random.nextDouble() < 0.4) IdPools.BASE_TIME.minus(random.nextInt(1, 181).toLong(), java.time.temporal.ChronoUnit.DAYS).toString() else null,
                )
            }
        }

        val graph = IdPools.graph(
            TenantCoreDataset(profile.name, profile.seed, organizations, users, memberships, projects, auditEvents, apiKeys, invitations)
        )
        projects.forEach { project ->
            val memberIds = orgMemberMap.getValue(project.orgId)
            val orgMemberships = graph.membershipsByOrg[project.orgId].orEmpty()
            val orgApiKeys = graph.apiKeysByOrg[project.orgId].orEmpty()
            val orgInvitations = graph.invitationsByOrg[project.orgId].orEmpty()
            repeat(Distributions.auditEventCount(random, project.status)) {
                val userId = memberIds.random(random)
                val membership = graph.membershipByOrgUser.getValue("${project.orgId}:$userId")
                val floor = maxOf(java.time.Instant.parse(project.createdAt), java.time.Instant.parse(membership.joinedAt))
                var resourceType = Distributions.weightedResourceType(random)
                val resourceId = when (resourceType) {
                    "user" -> userId
                    "membership" -> orgMemberships.random(random).id
                    "api_key" -> orgApiKeys.randomOrNull()?.id ?: project.id.also { resourceType = "project" }
                    "invitation" -> orgInvitations.randomOrNull()?.id ?: project.id.also { resourceType = "project" }
                    else -> project.id
                }
                auditEvents += AuditEvent(
                    id = IdPools.deterministicId(random),
                    orgId = project.orgId,
                    userId = userId,
                    projectId = project.id,
                    action = Distributions.weightedAuditAction(random),
                    resourceType = resourceType,
                    resourceId = resourceId,
                    ts = IdPools.between(random, floor, IdPools.BASE_TIME).toString(),
                )
            }
        }

        return TenantCoreDataset(
            profileName = profile.name,
            seed = profile.seed,
            organizations = organizations,
            users = users,
            memberships = memberships,
            projects = projects,
            auditEvents = auditEvents.sortedBy { it.ts },
            apiKeys = apiKeys,
            invitations = invitations,
        )
    }

    private fun uniqueEmail(seen: MutableSet<String>, localHint: String, domain: String, random: Random): String {
        var candidate = "${IdPools.slugify(localHint)}@$domain"
        while (!seen.add(candidate.lowercase())) {
            candidate = "${IdPools.slugify(localHint)}${random.nextInt(1, 9999)}@$domain"
        }
        return candidate
    }

    private fun randomKey(random: Random): String =
        buildString(8) { repeat(8) { append(KEY_ALPHABET[random.nextInt(KEY_ALPHABET.length)]) } }

    private fun kotlinFakerAvailabilityNote(): String =
        try {
            // kotlin-faker offers a more idiomatic Kotlin DSL than Java-style providers.
            Class.forName("io.github.serpro69.kfaker.Faker")
            "kotlin-faker DSL available"
        } catch (_: Throwable) {
            "kotlin-faker DSL unavailable"
        }
}
