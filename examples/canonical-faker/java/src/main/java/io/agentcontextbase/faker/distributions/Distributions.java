package io.agentcontextbase.faker.distributions;

import java.util.Random;

public final class Distributions {
    private Distributions() {
    }

    public static String weightedPlan(Random random) {
        return pick(random, "free", "free", "free", "free", "free", "pro", "pro", "pro", "pro", "enterprise");
    }

    public static String weightedRegion(Random random) {
        return pick(random, "us-east", "us-east", "us-east", "us-east", "us-west", "us-west", "eu-west", "eu-west", "ap-southeast");
    }

    public static String weightedLocale(Random random) {
        return pick(random, "en-US", "en-US", "en-US", "en-US", "en-US", "en-US", "en-GB", "en-GB", "de-DE", "fr-FR");
    }

    public static String weightedMembershipRole(Random random) {
        return pick(random, "admin", "member", "member", "member", "member", "member", "member", "viewer", "viewer", "viewer");
    }

    public static String weightedProjectStatus(Random random) {
        return pick(random, "active", "active", "active", "active", "active", "active", "archived", "archived", "draft", "draft");
    }

    public static String weightedInvitationRole(Random random) {
        return pick(random, "admin", "member", "member", "member", "viewer", "viewer");
    }

    public static String weightedAuditAction(Random random) {
        return pick(random, "created", "created", "updated", "updated", "updated", "deleted", "archived", "invited", "exported");
    }

    public static String weightedResourceType(Random random) {
        return pick(random, "project", "project", "project", "user", "membership", "membership", "api_key", "invitation");
    }

    public static int memberCount(Random random, int userCount) {
        int max = Math.max(3, Math.min(userCount, 8));
        return 3 + random.nextInt(max - 3 + 1);
    }

    public static int projectCount(Random random) {
        return 2 + random.nextInt(3);
    }

    public static int apiKeyCount(Random random) {
        return 1 + random.nextInt(2);
    }

    public static int invitationCount(Random random) {
        return 1 + random.nextInt(2);
    }

    public static int auditEventCount(Random random, String status) {
        return switch (status) {
            case "active" -> 8 + random.nextInt(7);
            case "archived" -> 4 + random.nextInt(5);
            default -> 3 + random.nextInt(3);
        };
    }

    private static String pick(Random random, String... values) {
        return values[random.nextInt(values.length)];
    }
}
