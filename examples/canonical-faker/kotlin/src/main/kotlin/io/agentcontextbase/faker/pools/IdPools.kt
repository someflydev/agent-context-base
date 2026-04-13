package io.agentcontextbase.faker.pools

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import io.agentcontextbase.faker.domain.ApiKey
import io.agentcontextbase.faker.domain.Invitation
import io.agentcontextbase.faker.domain.Membership
import io.agentcontextbase.faker.domain.TenantCoreDataset
import io.agentcontextbase.faker.validate.ValidationReport
import java.nio.file.Files
import java.nio.file.Path
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.UUID
import kotlin.random.Random

object IdPools {
    val BASE_TIME: Instant = Instant.parse("2026-01-01T12:00:00Z")
    val TIMEZONE_BY_LOCALE: Map<String, String> = mapOf(
        "en-US" to "America/New_York",
        "en-GB" to "Europe/London",
        "de-DE" to "Europe/Berlin",
        "fr-FR" to "Europe/Paris",
    )
    private val mapper = jacksonObjectMapper()

    fun slugify(value: String): String =
        value.lowercase().replace(Regex("[^a-z0-9]+"), "-").trim('-').ifBlank { "tenantcore" }

    fun deterministicId(random: Random): String {
        val bytes = ByteArray(16)
        random.nextBytes(bytes)
        return UUID.nameUUIDFromBytes(bytes).toString()
    }

    fun boundedPast(random: Random): Instant = BASE_TIME.minus(random.nextInt(0, 365 * 3 + 1).toLong(), ChronoUnit.DAYS)

    fun between(random: Random, start: Instant, end: Instant): Instant {
        val startEpoch = start.epochSecond
        val endEpoch = end.epochSecond
        if (startEpoch >= endEpoch) return start
        return Instant.ofEpochSecond(random.nextLong(startEpoch, endEpoch + 1))
    }

    fun writeJsonl(outputDir: Path, dataset: TenantCoreDataset, report: ValidationReport) {
        Files.createDirectories(outputDir)
        writeRows(outputDir.resolve("organizations.jsonl"), dataset.organizations)
        writeRows(outputDir.resolve("users.jsonl"), dataset.users)
        writeRows(outputDir.resolve("memberships.jsonl"), dataset.memberships)
        writeRows(outputDir.resolve("projects.jsonl"), dataset.projects)
        writeRows(outputDir.resolve("audit_events.jsonl"), dataset.auditEvents)
        writeRows(outputDir.resolve("api_keys.jsonl"), dataset.apiKeys)
        writeRows(outputDir.resolve("invitations.jsonl"), dataset.invitations)
        mapper.writerWithDefaultPrettyPrinter().writeValue(outputDir.resolve("${dataset.profileName}-report.json").toFile(), report)
    }

    private fun writeRows(path: Path, rows: List<Any>) {
        Files.newBufferedWriter(path).use { writer ->
            rows.forEach { row ->
                writer.write(mapper.writeValueAsString(row))
                writer.newLine()
            }
        }
    }

    data class GraphIndex(
        val orgMemberMap: Map<String, List<String>>,
        val userEmailById: Map<String, String>,
        val membershipByOrgUser: Map<String, Membership>,
        val membershipsByOrg: Map<String, List<Membership>>,
        val apiKeysByOrg: Map<String, List<ApiKey>>,
        val invitationsByOrg: Map<String, List<Invitation>>,
    )

    fun graph(dataset: TenantCoreDataset): GraphIndex {
        val orgMemberMap = mutableMapOf<String, MutableList<String>>()
        val userEmailById = dataset.users.associate { it.id to it.email.lowercase() }
        val membershipByOrgUser = mutableMapOf<String, Membership>()
        val membershipsByOrg = mutableMapOf<String, MutableList<Membership>>()
        val apiKeysByOrg = mutableMapOf<String, MutableList<ApiKey>>()
        val invitationsByOrg = mutableMapOf<String, MutableList<Invitation>>()

        dataset.memberships.forEach { membership ->
            orgMemberMap.getOrPut(membership.orgId) { mutableListOf() }.add(membership.userId)
            membershipByOrgUser["${membership.orgId}:${membership.userId}"] = membership
            membershipsByOrg.getOrPut(membership.orgId) { mutableListOf() }.add(membership)
        }
        dataset.apiKeys.forEach { apiKey ->
            apiKeysByOrg.getOrPut(apiKey.orgId) { mutableListOf() }.add(apiKey)
        }
        dataset.invitations.forEach { invitation ->
            invitationsByOrg.getOrPut(invitation.orgId) { mutableListOf() }.add(invitation)
        }
        return GraphIndex(
            orgMemberMap = orgMemberMap,
            userEmailById = userEmailById,
            membershipByOrgUser = membershipByOrgUser,
            membershipsByOrg = membershipsByOrg,
            apiKeysByOrg = apiKeysByOrg,
            invitationsByOrg = invitationsByOrg,
        )
    }
}
