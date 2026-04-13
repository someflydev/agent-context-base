package io.agentcontextbase.faker.pools;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import io.agentcontextbase.faker.domain.TenantCoreEntities;
import io.agentcontextbase.faker.validate.ValidationReport;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.UUID;

public final class IdPools {
    public static final Instant BASE_TIME = Instant.parse("2026-01-01T12:00:00Z");
    public static final Map<String, String> TIMEZONE_BY_LOCALE = Map.of(
            "en-US", "America/New_York",
            "en-GB", "Europe/London",
            "de-DE", "Europe/Berlin",
            "fr-FR", "Europe/Paris"
    );
    private static final ObjectMapper MAPPER = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);

    private IdPools() {
    }

    public static String slugify(String value) {
        String normalized = value.toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+", "-");
        normalized = normalized.replaceAll("^-+", "").replaceAll("-+$", "");
        return normalized.isBlank() ? "tenantcore" : normalized;
    }

    public static String deterministicId(Random random) {
        byte[] bytes = new byte[16];
        random.nextBytes(bytes);
        return UUID.nameUUIDFromBytes(bytes).toString();
    }

    public static Instant boundedPast(Random random) {
        return BASE_TIME.minus(3L * 365 - random.nextInt(365 * 3 + 1), ChronoUnit.DAYS);
    }

    public static Instant between(Random random, Instant start, Instant end) {
        long startEpoch = start.getEpochSecond();
        long endEpoch = end.getEpochSecond();
        if (startEpoch >= endEpoch) {
            return start;
        }
        long delta = startEpoch + Math.abs(random.nextLong()) % (endEpoch - startEpoch + 1);
        return Instant.ofEpochSecond(delta);
    }

    public static void writeJsonl(Path outputDir, TenantCoreEntities.TenantCoreDataset dataset, ValidationReport report) throws IOException {
        Files.createDirectories(outputDir);
        writeRows(outputDir.resolve("organizations.jsonl"), dataset.organizations());
        writeRows(outputDir.resolve("users.jsonl"), dataset.users());
        writeRows(outputDir.resolve("memberships.jsonl"), dataset.memberships());
        writeRows(outputDir.resolve("projects.jsonl"), dataset.projects());
        writeRows(outputDir.resolve("audit_events.jsonl"), dataset.auditEvents());
        writeRows(outputDir.resolve("api_keys.jsonl"), dataset.apiKeys());
        writeRows(outputDir.resolve("invitations.jsonl"), dataset.invitations());
        MAPPER.writeValue(outputDir.resolve(dataset.profileName() + "-report.json").toFile(), report);
    }

    private static void writeRows(Path path, List<?> rows) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(path)) {
            for (Object row : rows) {
                writer.write(MAPPER.writeValueAsString(row));
                writer.newLine();
            }
        }
    }

    public static GraphIndex graph(TenantCoreEntities.TenantCoreDataset dataset) {
        Map<String, List<String>> orgMemberMap = new HashMap<>();
        Map<String, String> userEmailById = new HashMap<>();
        Map<String, TenantCoreEntities.Membership> membershipByOrgUser = new HashMap<>();
        Map<String, List<TenantCoreEntities.Membership>> membershipsByOrg = new HashMap<>();
        Map<String, List<TenantCoreEntities.ApiKey>> apiKeysByOrg = new HashMap<>();
        Map<String, List<TenantCoreEntities.Invitation>> invitationsByOrg = new HashMap<>();

        for (TenantCoreEntities.User user : dataset.users()) {
            userEmailById.put(user.id(), user.email().toLowerCase(Locale.ROOT));
        }
        for (TenantCoreEntities.Membership membership : dataset.memberships()) {
            orgMemberMap.computeIfAbsent(membership.orgId(), ignored -> new java.util.ArrayList<>()).add(membership.userId());
            membershipByOrgUser.put(membership.orgId() + ":" + membership.userId(), membership);
            membershipsByOrg.computeIfAbsent(membership.orgId(), ignored -> new java.util.ArrayList<>()).add(membership);
        }
        for (TenantCoreEntities.ApiKey apiKey : dataset.apiKeys()) {
            apiKeysByOrg.computeIfAbsent(apiKey.orgId(), ignored -> new java.util.ArrayList<>()).add(apiKey);
        }
        for (TenantCoreEntities.Invitation invitation : dataset.invitations()) {
            invitationsByOrg.computeIfAbsent(invitation.orgId(), ignored -> new java.util.ArrayList<>()).add(invitation);
        }
        return new GraphIndex(orgMemberMap, userEmailById, membershipByOrgUser, membershipsByOrg, apiKeysByOrg, invitationsByOrg);
    }

    public record GraphIndex(
            Map<String, List<String>> orgMemberMap,
            Map<String, String> userEmailById,
            Map<String, TenantCoreEntities.Membership> membershipByOrgUser,
            Map<String, List<TenantCoreEntities.Membership>> membershipsByOrg,
            Map<String, List<TenantCoreEntities.ApiKey>> apiKeysByOrg,
            Map<String, List<TenantCoreEntities.Invitation>> invitationsByOrg
    ) {
    }
}
