package io.agentcontextbase.faker.profiles;

public record Profile(String name, int numOrgs, int numUsers, long seed) {
    public static final Profile SMOKE = new Profile("smoke", 3, 10, 42);
    public static final Profile SMALL = new Profile("small", 20, 200, 1000);
    public static final Profile MEDIUM = new Profile("medium", 200, 5000, 5000);
    public static final Profile LARGE = new Profile("large", 2000, 50000, 9999);

    public static Profile resolve(String name, Long seedOverride) {
        Profile profile = switch (name) {
            case "small" -> SMALL;
            case "medium" -> MEDIUM;
            case "large" -> LARGE;
            default -> SMOKE;
        };
        if (seedOverride != null) {
            return new Profile(profile.name(), profile.numOrgs(), profile.numUsers(), seedOverride);
        }
        return profile;
    }
}
