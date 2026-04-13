package io.agentcontextbase.faker.pipeline;

import io.agentcontextbase.faker.distributions.Distributions;
import io.agentcontextbase.faker.domain.TenantCoreEntities;
import io.agentcontextbase.faker.pools.IdPools;
import io.agentcontextbase.faker.profiles.Profile;
import io.agentcontextbase.faker.validate.ValidationReport;
import net.datafaker.Faker;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.Set;

public final class TenantCorePipeline {
    private static final String[] EDGE_CASE_NAMES = {
            "Sofie D'Aubigne",
            "Bjorn Asmussen",
            "Francois L'Ecuyer",
            "Marta Nunez de la Pena",
            "Zoe Kruger-Renaud"
    };
    private static final char[] KEY_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789".toCharArray();

    private TenantCorePipeline() {
    }

    public static TenantCoreEntities.TenantCoreDataset generate(Profile profile) {
        Faker faker = new Faker(new Random(profile.seed()));
        Random random = new Random(profile.seed());

        List<TenantCoreEntities.Organization> organizations = new ArrayList<>();
        List<TenantCoreEntities.User> users = new ArrayList<>();
        List<TenantCoreEntities.Membership> memberships = new ArrayList<>();
        List<TenantCoreEntities.Project> projects = new ArrayList<>();
        List<TenantCoreEntities.ApiKey> apiKeys = new ArrayList<>();
        List<TenantCoreEntities.Invitation> invitations = new ArrayList<>();
        List<TenantCoreEntities.AuditEvent> auditEvents = new ArrayList<>();

        Set<String> orgSlugs = new HashSet<>();
        Set<String> orgEmails = new HashSet<>();
        Set<String> userEmails = new HashSet<>();
        Set<String> keyPrefixes = new HashSet<>();
        Map<String, List<String>> orgIds = new HashMap<>();

        for (int index = 0; index < profile.numOrgs(); index++) {
            String name = faker.company().name() + " Tenant " + (index + 1);
            String baseSlug = IdPools.slugify(name);
            String slug = baseSlug;
            for (int suffix = 2; orgSlugs.contains(slug); suffix++) {
                slug = baseSlug + "-" + suffix;
            }
            orgSlugs.add(slug);
            String ownerEmail = uniqueEmail(faker, orgEmails, "owner" + (index + 1), "tenantcore-example.test");
            organizations.add(new TenantCoreEntities.Organization(
                    IdPools.deterministicId(random),
                    name,
                    slug,
                    Distributions.weightedPlan(random),
                    Distributions.weightedRegion(random),
                    IdPools.boundedPast(random).toString(),
                    ownerEmail
            ));
        }

        for (int index = 0; index < profile.numUsers(); index++) {
            String locale = Distributions.weightedLocale(random);
            boolean edgeCase = random.nextDouble() < 0.05;
            String email = uniqueEmail(
                    faker,
                    userEmails,
                    edgeCase ? "edgecase" + index : faker.name().username().toLowerCase(Locale.ROOT),
                    locale.toLowerCase(Locale.ROOT).replace("-", "") + ".tenantcore-example.test"
            );
            users.add(new TenantCoreEntities.User(
                    IdPools.deterministicId(random),
                    email,
                    edgeCase ? EDGE_CASE_NAMES[index % EDGE_CASE_NAMES.length] : faker.name().fullName(),
                    locale,
                    edgeCase ? "UTC" : IdPools.TIMEZONE_BY_LOCALE.get(locale),
                    IdPools.boundedPast(random).toString()
            ));
        }

        for (TenantCoreEntities.Organization organization : organizations) {
            List<TenantCoreEntities.User> sampledUsers = sampleUsers(users, Distributions.memberCount(random, users.size()), random);
            List<String> memberIds = new ArrayList<>();
            for (int position = 0; position < sampledUsers.size(); position++) {
                TenantCoreEntities.User user = sampledUsers.get(position);
                String invitedBy = position == 0 ? null : memberIds.get(random.nextInt(memberIds.size()));
                memberIds.add(user.id());
                memberships.add(new TenantCoreEntities.Membership(
                        IdPools.deterministicId(random),
                        organization.id(),
                        user.id(),
                        position == 0 ? "owner" : Distributions.weightedMembershipRole(random),
                        IdPools.between(random, Instant.parse(organization.createdAt()), IdPools.BASE_TIME).toString(),
                        invitedBy
                ));
            }
            orgIds.put(organization.id(), memberIds);
        }

        for (TenantCoreEntities.Organization organization : organizations) {
            List<String> memberIds = orgIds.get(organization.id());
            for (int index = 0; index < Distributions.projectCount(random); index++) {
                projects.add(new TenantCoreEntities.Project(
                        IdPools.deterministicId(random),
                        organization.id(),
                        faker.commerce().productName(),
                        Distributions.weightedProjectStatus(random),
                        memberIds.get(random.nextInt(memberIds.size())),
                        IdPools.between(random, Instant.parse(organization.createdAt()), IdPools.BASE_TIME).toString()
                ));
            }
        }

        TenantCoreEntities.TenantCoreDataset projectDataset = new TenantCoreEntities.TenantCoreDataset(
                profile.name(), profile.seed(), organizations, users, memberships, projects, auditEvents, apiKeys, invitations
        );
        IdPools.GraphIndex projectGraph = IdPools.graph(projectDataset);

        for (TenantCoreEntities.Organization organization : organizations) {
            List<String> memberIds = orgIds.get(organization.id());
            Set<String> memberEmails = new HashSet<>();
            for (String memberId : memberIds) {
                memberEmails.add(projectGraph.userEmailById().get(memberId));
            }
            for (int index = 0; index < Distributions.apiKeyCount(random); index++) {
                String prefix = "tc_" + randomKey(random);
                while (keyPrefixes.contains(prefix)) {
                    prefix = "tc_" + randomKey(random);
                }
                keyPrefixes.add(prefix);
                Instant createdAt = IdPools.between(random, Instant.parse(organization.createdAt()), IdPools.BASE_TIME);
                apiKeys.add(new TenantCoreEntities.ApiKey(
                        IdPools.deterministicId(random),
                        organization.id(),
                        memberIds.get(random.nextInt(memberIds.size())),
                        faker.company().buzzword(),
                        prefix,
                        createdAt.toString(),
                        random.nextDouble() < 0.7 ? IdPools.between(random, createdAt, IdPools.BASE_TIME).toString() : null
                ));
            }
            for (int index = 0; index < Distributions.invitationCount(random); index++) {
                String invitedEmail = faker.internet().emailAddress().toLowerCase(Locale.ROOT);
                while (memberEmails.contains(invitedEmail)) {
                    invitedEmail = faker.internet().emailAddress().toLowerCase(Locale.ROOT);
                }
                invitations.add(new TenantCoreEntities.Invitation(
                        IdPools.deterministicId(random),
                        organization.id(),
                        invitedEmail,
                        Distributions.weightedInvitationRole(random),
                        memberIds.get(random.nextInt(memberIds.size())),
                        IdPools.BASE_TIME.plus(1 + random.nextInt(30), ChronoUnit.DAYS).toString(),
                        random.nextDouble() < 0.4 ? IdPools.BASE_TIME.minus(1 + random.nextInt(180), ChronoUnit.DAYS).toString() : null
                ));
            }
        }

        TenantCoreEntities.TenantCoreDataset supportDataset = new TenantCoreEntities.TenantCoreDataset(
                profile.name(), profile.seed(), organizations, users, memberships, projects, auditEvents, apiKeys, invitations
        );
        IdPools.GraphIndex graph = IdPools.graph(supportDataset);

        for (TenantCoreEntities.Project project : projects) {
            List<String> memberIds = orgIds.get(project.orgId());
            List<TenantCoreEntities.Membership> orgMemberships = graph.membershipsByOrg().get(project.orgId());
            List<TenantCoreEntities.ApiKey> orgApiKeys = graph.apiKeysByOrg().getOrDefault(project.orgId(), List.of());
            List<TenantCoreEntities.Invitation> orgInvitations = graph.invitationsByOrg().getOrDefault(project.orgId(), List.of());
            for (int index = 0; index < Distributions.auditEventCount(random, project.status()); index++) {
                String userId = memberIds.get(random.nextInt(memberIds.size()));
                TenantCoreEntities.Membership membership = graph.membershipByOrgUser().get(project.orgId() + ":" + userId);
                Instant floor = max(Instant.parse(project.createdAt()), Instant.parse(membership.joinedAt()));
                String resourceType = Distributions.weightedResourceType(random);
                String resourceId = switch (resourceType) {
                    case "user" -> userId;
                    case "membership" -> orgMemberships.get(random.nextInt(orgMemberships.size())).id();
                    case "api_key" -> orgApiKeys.isEmpty() ? project.id() : orgApiKeys.get(random.nextInt(orgApiKeys.size())).id();
                    case "invitation" -> orgInvitations.isEmpty() ? project.id() : orgInvitations.get(random.nextInt(orgInvitations.size())).id();
                    default -> project.id();
                };
                if ("api_key".equals(resourceType) && orgApiKeys.isEmpty()) {
                    resourceType = "project";
                }
                if ("invitation".equals(resourceType) && orgInvitations.isEmpty()) {
                    resourceType = "project";
                }
                auditEvents.add(new TenantCoreEntities.AuditEvent(
                        IdPools.deterministicId(random),
                        project.orgId(),
                        userId,
                        project.id(),
                        Distributions.weightedAuditAction(random),
                        resourceType,
                        resourceId,
                        IdPools.between(random, floor, IdPools.BASE_TIME).toString()
                ));
            }
        }

        auditEvents.sort(Comparator.comparing(TenantCoreEntities.AuditEvent::ts));
        return new TenantCoreEntities.TenantCoreDataset(
                profile.name(), profile.seed(), organizations, users, memberships, projects, auditEvents, apiKeys, invitations
        );
    }

    public static ValidationReport validate(TenantCoreEntities.TenantCoreDataset dataset) {
        List<String> violations = new ArrayList<>();
        Map<String, Integer> counts = new HashMap<>();
        counts.put("organizations", dataset.organizations().size());
        counts.put("users", dataset.users().size());
        counts.put("memberships", dataset.memberships().size());
        counts.put("projects", dataset.projects().size());
        counts.put("audit_events", dataset.auditEvents().size());
        counts.put("api_keys", dataset.apiKeys().size());
        counts.put("invitations", dataset.invitations().size());

        Map<String, TenantCoreEntities.Organization> orgs = new HashMap<>();
        for (TenantCoreEntities.Organization org : dataset.organizations()) {
            if (orgs.put(org.id(), org) != null) {
                violations.add("duplicate organizations.id: " + org.id());
            }
        }
        Map<String, TenantCoreEntities.User> users = new HashMap<>();
        Set<String> seenEmails = new HashSet<>();
        for (TenantCoreEntities.User user : dataset.users()) {
            users.put(user.id(), user);
            if (!seenEmails.add(user.email().toLowerCase(Locale.ROOT))) {
                violations.add("duplicate users.email: " + user.email());
            }
        }

        Set<String> membershipIds = new HashSet<>();
        for (TenantCoreEntities.Membership membership : dataset.memberships()) {
            membershipIds.add(membership.id());
            TenantCoreEntities.Organization org = orgs.get(membership.orgId());
            if (org == null) {
                violations.add("membership missing org: " + membership.id());
                continue;
            }
            if (!users.containsKey(membership.userId())) {
                violations.add("membership missing user: " + membership.id());
                continue;
            }
            if (Instant.parse(membership.joinedAt()).isBefore(Instant.parse(org.createdAt()))) {
                violations.add("Rule A violated by membership " + membership.id());
            }
            if (membership.invitedBy() != null && !users.containsKey(membership.invitedBy())) {
                violations.add("membership invited_by missing user: " + membership.id());
            }
        }

        Map<String, TenantCoreEntities.Project> projects = new HashMap<>();
        for (TenantCoreEntities.Project project : dataset.projects()) {
            projects.put(project.id(), project);
            TenantCoreEntities.Organization org = orgs.get(project.orgId());
            if (org == null) {
                violations.add("project missing org: " + project.id());
                continue;
            }
            if (Instant.parse(project.createdAt()).isBefore(Instant.parse(org.createdAt()))) {
                violations.add("Rule B violated by project " + project.id());
            }
        }

        IdPools.GraphIndex graph = IdPools.graph(dataset);
        Set<String> apiKeyIds = new HashSet<>();
        Set<String> keyPrefixes = new HashSet<>();
        for (TenantCoreEntities.ApiKey apiKey : dataset.apiKeys()) {
            apiKeyIds.add(apiKey.id());
            if (!graph.orgMemberMap().getOrDefault(apiKey.orgId(), List.of()).contains(apiKey.createdBy())) {
                violations.add("Rule G violated by api_key " + apiKey.id());
            }
            if (!keyPrefixes.add(apiKey.keyPrefix())) {
                violations.add("duplicate api_key.key_prefix: " + apiKey.keyPrefix());
            }
            if (apiKey.lastUsedAt() != null && Instant.parse(apiKey.lastUsedAt()).isBefore(Instant.parse(apiKey.createdAt()))) {
                violations.add("api_key last_used_at before created_at: " + apiKey.id());
            }
        }

        Set<String> invitationIds = new HashSet<>();
        for (TenantCoreEntities.Invitation invitation : dataset.invitations()) {
            invitationIds.add(invitation.id());
            if (!graph.orgMemberMap().getOrDefault(invitation.orgId(), List.of()).contains(invitation.invitedBy())) {
                violations.add("Rule H violated by invitation " + invitation.id());
            }
            boolean matchesMember = graph.orgMemberMap().getOrDefault(invitation.orgId(), List.of()).stream()
                    .map(graph.userEmailById()::get)
                    .anyMatch(email -> invitation.invitedEmail().equalsIgnoreCase(email));
            if (matchesMember) {
                violations.add("Rule I violated by invitation " + invitation.id());
            }
            Instant expiresAt = Instant.parse(invitation.expiresAt());
            if (!expiresAt.isAfter(IdPools.BASE_TIME)) {
                violations.add("invitation expiry must be in the future: " + invitation.id());
            }
            if (expiresAt.isAfter(IdPools.BASE_TIME.plus(30, ChronoUnit.DAYS))) {
                violations.add("invitation expiry must be within 30 days: " + invitation.id());
            }
            if (invitation.acceptedAt() != null && Instant.parse(invitation.acceptedAt()).isAfter(IdPools.BASE_TIME)) {
                violations.add("invitation accepted_at must be in the past: " + invitation.id());
            }
        }

        for (TenantCoreEntities.Project project : dataset.projects()) {
            if (!graph.orgMemberMap().getOrDefault(project.orgId(), List.of()).contains(project.createdBy())) {
                violations.add("Rule C violated by project " + project.id());
            }
        }

        for (TenantCoreEntities.AuditEvent event : dataset.auditEvents()) {
            TenantCoreEntities.Project project = projects.get(event.projectId());
            if (project == null) {
                violations.add("audit_event missing project: " + event.id());
                continue;
            }
            if (!graph.orgMemberMap().getOrDefault(event.orgId(), List.of()).contains(event.userId())) {
                violations.add("Rule D violated by audit_event " + event.id());
            }
            if (!project.orgId().equals(event.orgId())) {
                violations.add("Rule E violated by audit_event " + event.id());
            }
            if (Instant.parse(event.ts()).isBefore(Instant.parse(project.createdAt()))) {
                violations.add("Rule F violated by audit_event " + event.id());
            }
            TenantCoreEntities.Membership membership = graph.membershipByOrgUser().get(event.orgId() + ":" + event.userId());
            if (membership != null && Instant.parse(event.ts()).isBefore(Instant.parse(membership.joinedAt()))) {
                violations.add("audit event before membership joined_at: " + event.id());
            }
            switch (event.resourceType()) {
                case "project" -> {
                    if (!projects.containsKey(event.resourceId())) {
                        violations.add("audit event resource project missing: " + event.id());
                    }
                }
                case "user" -> {
                    if (!users.containsKey(event.resourceId())) {
                        violations.add("audit event resource user missing: " + event.id());
                    }
                }
                case "membership" -> {
                    if (!membershipIds.contains(event.resourceId())) {
                        violations.add("audit event resource membership missing: " + event.id());
                    }
                }
                case "api_key" -> {
                    if (!apiKeyIds.contains(event.resourceId())) {
                        violations.add("audit event resource api_key missing: " + event.id());
                    }
                }
                case "invitation" -> {
                    if (!invitationIds.contains(event.resourceId())) {
                        violations.add("audit event resource invitation missing: " + event.id());
                    }
                }
                default -> {
                }
            }
        }

        return new ValidationReport(violations.isEmpty(), violations, counts, dataset.seed(), dataset.profileName());
    }

    private static List<TenantCoreEntities.User> sampleUsers(List<TenantCoreEntities.User> users, int count, Random random) {
        List<TenantCoreEntities.User> copy = new ArrayList<>(users);
        java.util.Collections.shuffle(copy, random);
        return copy.subList(0, count);
    }

    private static String uniqueEmail(Faker faker, Set<String> seen, String localHint, String domain) {
        String email = IdPools.slugify(localHint) + "@" + domain;
        while (!seen.add(email)) {
            email = faker.internet().username().toLowerCase(Locale.ROOT) + "@" + domain;
        }
        return email;
    }

    private static String randomKey(Random random) {
        StringBuilder builder = new StringBuilder(8);
        for (int index = 0; index < 8; index++) {
            builder.append(KEY_ALPHABET[random.nextInt(KEY_ALPHABET.length)]);
        }
        return builder.toString();
    }

    private static Instant max(Instant left, Instant right) {
        return left.isAfter(right) ? left : right;
    }
}
