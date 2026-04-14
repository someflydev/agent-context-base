package io.agentcontextbase.faker

import net.datafaker.Faker
import java.time.format.DateTimeFormatter
import java.time.{Instant, ZoneOffset, ZoneId}
import java.util.concurrent.TimeUnit
import scala.util.Random

object Pipeline {
  private val formatter = DateTimeFormatter.ISO_INSTANT

  def generate(profile: Profile): Dataset = {
    val rng = new Random(profile.seed)
    val faker = new Faker(new java.util.Random(profile.seed))

    // ZIO Stream could replace LazyList for medium/large profiles
    // when backpressure and async chunked writes matter.

    val orgs = buildOrgs(profile.numOrgs, faker, rng)
    val users = buildUsers(profile.numUsers, faker, rng)

    val (memberships, orgMemberMap) = buildMemberships(orgs, users, rng)
    val (projects, projectOrgMap) = buildProjects(orgs, orgMemberMap, faker, rng)
    val apiKeys = buildApiKeys(orgs, orgMemberMap, faker, rng)
    val invitations = buildInvitations(orgs, orgMemberMap, users, faker, rng)
    val auditEvents = buildAuditEvents(projects, orgMemberMap, projectOrgMap, apiKeys, invitations, rng)

    val dataset = Dataset(
      organizations = orgs.toVector,
      users = users.toVector,
      memberships = memberships.toVector,
      projects = projects.toVector,
      audit_events = auditEvents.toVector,
      api_keys = apiKeys.toVector,
      invitations = invitations.toVector
    )

    val report = Validate.check(dataset).copy(seed = profile.seed, profileName = profile.name)
    if (!report.ok) {
      throw new RuntimeException(s"Validation failed: ${report.violations.mkString(", ")}")
    }

    dataset.copy(report = Some(report))
  }

  private def buildOrgs(count: Int, faker: Faker, rng: Random): LazyList[Organization] = {
    var seenSlugs = Set.empty[String]
    var seenEmails = Set.empty[String]

    LazyList.continually {
      val name = faker.company().name()
      val baseSlug = name.toLowerCase.replaceAll("[^a-z0-9]+", "-").stripMargin('-')
      var slug = baseSlug
      var suffix = 1
      while (seenSlugs.contains(slug)) {
        slug = s"$baseSlug-$suffix"
        suffix += 1
      }
      seenSlugs += slug

      var email = faker.internet().emailAddress()
      while (seenEmails.contains(email)) {
        email = faker.internet().emailAddress()
      }
      seenEmails += email

      val plan = Distributions.weightedPlan(rng)
      val region = Distributions.weightedRegion(rng)
      
      val baseDate = Instant.parse("2024-01-01T00:00:00Z").toEpochMilli
      val range = 3L * 365 * 24 * 60 * 60 * 1000
      val createdAtInstant = baseDate - (rng.nextDouble() * range).toLong
      val createdAt = Instant.ofEpochMilli(createdAtInstant).toString

      Organization(
        id = Pools.deterministicUuid(rng),
        name = name,
        slug = slug,
        plan = plan,
        region = region,
        created_at = createdAt,
        owner_email = email
      )
    }.take(count)
  }

  private def buildUsers(count: Int, faker: Faker, rng: Random): LazyList[User] = {
    var seenEmails = Set.empty[String]
    LazyList.continually {
      var email = faker.internet().emailAddress()
      while (seenEmails.contains(email)) {
        email = faker.internet().emailAddress()
      }
      seenEmails += email

      val fullName = faker.name().fullName()
      val locale = if (rng.nextDouble() < 0.6) "en-US" else "en-GB"
      val timezone = if (locale == "en-US") "America/New_York" else "Europe/London"
      
      val baseDate = Instant.parse("2024-01-01T00:00:00Z").toEpochMilli
      val range = 3L * 365 * 24 * 60 * 60 * 1000
      val createdAtInstant = baseDate - (rng.nextDouble() * range).toLong
      val createdAt = Instant.ofEpochMilli(createdAtInstant).toString

      User(
        id = Pools.deterministicUuid(rng),
        email = email,
        full_name = fullName,
        locale = locale,
        timezone = timezone,
        created_at = createdAt
      )
    }.take(count)
  }

  private def buildMemberships(
    orgs: LazyList[Organization],
    users: LazyList[User],
    rng: Random
  ): (LazyList[Membership], Map[String, Vector[String]]) = {
    val allUserIds = users.map(_.id).toVector
    var memberships = Vector.empty[Membership]
    var orgMemberMap = Map.empty[String, Vector[String]]

    orgs.foreach { org =>
      val numMembers = 3 + rng.nextInt(48) // 3 to 50
      val memberIds = rng.shuffle(allUserIds).take(numMembers)
      orgMemberMap += (org.id -> memberIds)

      val orgMemberships = memberIds.zipWithIndex.map { case (userId, idx) =>
        val role = if (idx == 0) "owner" else Distributions.weightedRole(rng)
        val invitedBy = if (idx == 0) "" else memberIds(0) // first is owner

        val orgCreatedInstant = Instant.parse(org.created_at).toEpochMilli
        val now = Instant.parse("2024-01-01T00:00:00Z").toEpochMilli
        val range = math.max(1000L, now - orgCreatedInstant)
        val joinedAtInstant = orgCreatedInstant + (rng.nextDouble() * range).toLong
        val joinedAt = Instant.ofEpochMilli(joinedAtInstant).toString

        Membership(
          id = Pools.deterministicUuid(rng),
          org_id = org.id,
          user_id = userId,
          role = role,
          joined_at = joinedAt,
          invited_by = invitedBy
        )
      }
      memberships ++= orgMemberships
    }

    (memberships.to(LazyList), orgMemberMap)
  }

  private def buildProjects(
    orgs: LazyList[Organization],
    orgMemberMap: Map[String, Vector[String]],
    faker: Faker,
    rng: Random
  ): (LazyList[Project], Map[String, String]) = {
    var projects = Vector.empty[Project]
    var projectOrgMap = Map.empty[String, String]

    orgs.foreach { org =>
      val numProjects = 1 + rng.nextInt(20) // 1 to 20
      val memberIds = orgMemberMap(org.id)

      val orgProjects = (1 to numProjects).map { _ =>
        val createdBy = memberIds(rng.nextInt(memberIds.length))
        val status = Distributions.weightedProjectStatus(rng)

        val orgCreatedInstant = Instant.parse(org.created_at).toEpochMilli
        val now = Instant.parse("2024-01-01T00:00:00Z").toEpochMilli
        val range = math.max(1000L, now - orgCreatedInstant)
        val createdAtInstant = orgCreatedInstant + (rng.nextDouble() * range).toLong
        val createdAt = Instant.ofEpochMilli(createdAtInstant).toString

        val p = Project(
          id = Pools.deterministicUuid(rng),
          org_id = org.id,
          name = faker.app().name(),
          status = status,
          created_by = createdBy,
          created_at = createdAt
        )
        projectOrgMap += (p.id -> org.id)
        p
      }
      projects ++= orgProjects
    }

    (projects.to(LazyList), projectOrgMap)
  }

  private def buildApiKeys(
    orgs: LazyList[Organization],
    orgMemberMap: Map[String, Vector[String]],
    faker: Faker,
    rng: Random
  ): LazyList[ApiKey] = {
    orgs.flatMap { org =>
      val numKeys = rng.nextInt(11) // 0 to 10
      val memberIds = orgMemberMap(org.id)
      if (memberIds.isEmpty) Seq.empty
      else {
        (1 to numKeys).map { _ =>
          val createdBy = memberIds(rng.nextInt(memberIds.length))

          val orgCreatedInstant = Instant.parse(org.created_at).toEpochMilli
          val now = Instant.parse("2024-01-01T00:00:00Z").toEpochMilli
          val range = math.max(1000L, now - orgCreatedInstant)
          val createdAtInstant = orgCreatedInstant + (rng.nextDouble() * range).toLong
          val createdAt = Instant.ofEpochMilli(createdAtInstant).toString
          
          val lastUsedAtInstant = createdAtInstant + (rng.nextDouble() * (now - createdAtInstant)).toLong
          val lastUsedAt = if (rng.nextBoolean()) Instant.ofEpochMilli(lastUsedAtInstant).toString else null

          ApiKey(
            id = Pools.deterministicUuid(rng),
            org_id = org.id,
            created_by = createdBy,
            name = faker.lorem().word(),
            key_prefix = s"tc_${faker.internet().password(8, 8, true, true, true)}",
            created_at = createdAt,
            last_used_at = lastUsedAt
          )
        }
      }
    }
  }

  private def buildInvitations(
    orgs: LazyList[Organization],
    orgMemberMap: Map[String, Vector[String]],
    users: LazyList[User],
    faker: Faker,
    rng: Random
  ): LazyList[Invitation] = {
    val allEmails = users.map(_.email).toSet
    orgs.flatMap { org =>
      val numInvs = rng.nextInt(6) // 0 to 5
      val memberIds = orgMemberMap(org.id)
      if (memberIds.isEmpty) Seq.empty
      else {
        (1 to numInvs).map { _ =>
          val invitedBy = memberIds(rng.nextInt(memberIds.length))
          
          var email = faker.internet().emailAddress()
          while (allEmails.contains(email)) {
            email = faker.internet().emailAddress()
          }

          val baseDateStr = "2024-01-01T00:00:00Z"
          val baseDateInstant = Instant.parse(baseDateStr)
          val expiresAt = baseDateInstant.plusSeconds(rng.nextInt(30) * 86400L).toString
          val acceptedAt = if (rng.nextDouble() < 0.4) baseDateInstant.minusSeconds(rng.nextInt(30) * 86400L).toString else null

          Invitation(
            id = Pools.deterministicUuid(rng),
            org_id = org.id,
            invited_email = email,
            role = Distributions.weightedRole(rng),
            invited_by = invitedBy,
            expires_at = expiresAt,
            accepted_at = acceptedAt
          )
        }
      }
    }
  }

  private def buildAuditEvents(
    projects: LazyList[Project],
    orgMemberMap: Map[String, Vector[String]],
    projectOrgMap: Map[String, String],
    apiKeys: LazyList[ApiKey],
    invitations: LazyList[Invitation],
    rng: Random
  ): LazyList[AuditEvent] = {
    val apiKeysByOrg = apiKeys.groupBy(_.org_id)
    val invitationsByOrg = invitations.groupBy(_.org_id)

    projects.flatMap { proj =>
      val orgId = projectOrgMap(proj.id)
      val memberIds = orgMemberMap.getOrElse(orgId, Vector.empty)
      val orgApiKeys = apiKeysByOrg.getOrElse(orgId, Vector.empty)
      val orgInvitations = invitationsByOrg.getOrElse(orgId, Vector.empty)

      if (memberIds.isEmpty) Seq.empty
      else {
        val numEvents = 5 + rng.nextInt(496) // 5 to 500

        (1 to numEvents).map { _ =>
          val userId = memberIds(rng.nextInt(memberIds.length))
          val action = Distributions.weightedAction(rng)
          val resourceType = Distributions.weightedResourceType(rng)
          
          val resourceId = resourceType match {
            case "project" => proj.id
            case "membership" => Pools.deterministicUuid(rng) // Mocking resource id
            case "user" => userId
            case "api_key" => if (orgApiKeys.nonEmpty) orgApiKeys(rng.nextInt(orgApiKeys.length)).id else proj.id
            case "invitation" => if (orgInvitations.nonEmpty) orgInvitations(rng.nextInt(orgInvitations.length)).id else proj.id
            case _ => proj.id
          }

          val projCreatedInstant = Instant.parse(proj.created_at).toEpochMilli
          val now = Instant.parse("2024-01-01T00:00:00Z").toEpochMilli
          val range = math.max(1000L, now - projCreatedInstant)
          val tsInstant = projCreatedInstant + (rng.nextDouble() * range).toLong
          val ts = Instant.ofEpochMilli(tsInstant).toString

          AuditEvent(
            id = Pools.deterministicUuid(rng),
            org_id = orgId,
            user_id = userId,
            project_id = proj.id,
            action = action,
            resource_type = resourceType,
            resource_id = resourceId,
            ts = ts
          )
        }
      }
    }
  }
}
