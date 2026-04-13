package io.agentcontextbase.faker.profiles

data class Profile(
    val name: String,
    val numOrgs: Int,
    val numUsers: Int,
    val seed: Int,
) {
    companion object {
        val SMOKE = Profile("smoke", 3, 10, 42)
        val SMALL = Profile("small", 20, 200, 1000)
        val MEDIUM = Profile("medium", 200, 5000, 5000)
        val LARGE = Profile("large", 2000, 50000, 9999)

        fun resolve(name: String, seedOverride: Int?): Profile {
            val profile = when (name) {
                "small" -> SMALL
                "medium" -> MEDIUM
                "large" -> LARGE
                else -> SMOKE
            }
            return if (seedOverride != null) profile.copy(seed = seedOverride) else profile
        }
    }
}
