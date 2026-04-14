package io.agentcontextbase.faker

case class Profile(
  name: String,
  seed: Long,
  numOrgs: Int,
  numUsers: Int
)

object Profile {
  val SMOKE = Profile("smoke", 42L, 3, 10)
  val SMALL = Profile("small", 42L, 50, 500)
  val MEDIUM = Profile("medium", 42L, 500, 10000)
  val LARGE = Profile("large", 42L, 5000, 250000)

  def fromName(name: String): Profile = name.toLowerCase match {
    case "smoke" => SMOKE
    case "small" => SMALL
    case "medium" => MEDIUM
    case "large" => LARGE
    case _ => SMOKE
  }
}
