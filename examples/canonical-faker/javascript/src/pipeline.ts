import { faker } from "@faker-js/faker"
import Chance from "chance"
import type { ApiKey, AuditEvent, Dataset, Invitation, Membership, Organization, Project, User } from "./domain.js"
import type { Profile } from "./profiles.js"
import {
  addDays,
  BASE_TIME,
  buildPools,
  slugify,
  sortAuditEvents,
  TIMEZONE_BY_LOCALE,
  toIso,
  writeCsv,
  writeJsonl
} from "./pools.js"
import {
  apiKeyCount,
  auditEventCount,
  invitationCount,
  memberCount,
  pickAuditAction,
  pickInvitationRole,
  pickLocale,
  pickMembershipRole,
  pickPlan,
  pickProjectStatus,
  pickRegion,
  projectCount,
  withEdgeCase
} from "./distributions.js"
import { validateDataset } from "./validate.js"

const EDGE_CASE_NAMES = [
  "Sofie D'Aubigne",
  "Bjorn Asmussen",
  "Francois L'Ecuyer",
  "Marta Nunez de la Pena",
  "Zoe Kruger-Renaud"
] as const
const KEY_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"

function deterministicUuid(): string {
  return faker.string.uuid()
}

function pastDate(): Date {
  return faker.date.between({
    from: new Date(BASE_TIME.getTime() - 365 * 3 * 86400 * 1000),
    to: BASE_TIME
  })
}

function futureDate(): Date {
  return faker.date.between({
    from: new Date(BASE_TIME.getTime() + 1000),
    to: new Date(BASE_TIME.getTime() + 30 * 86400 * 1000)
  })
}

function between(from: Date, to: Date): Date {
  return faker.date.between({ from, to })
}

function longEmail(index: number, localeCode: string): string {
  const suffix = `.${localeCode.toLowerCase().replace("-", "")}.${index}@tenantcore-example.test`
  const localLength = 254 - suffix.length
  return `${`edgecase${index}`.slice(0, localLength).padEnd(localLength, "x")}${suffix}`
}

export async function generateDataset(profile: Profile): Promise<Dataset> {
  faker.seed(profile.seed)
  const chance = new Chance(profile.seed)

  const organizations: Organization[] = []
  const users: User[] = []
  const memberships: Membership[] = []
  const projects: Project[] = []
  const apiKeys: ApiKey[] = []
  const invitations: Invitation[] = []
  const auditEvents: AuditEvent[] = []

  const seenOrgSlugs = new Set<string>()
  const seenOrgEmails = new Set<string>()
  const seenUserEmails = new Set<string>()
  const seenPrefixes = new Set<string>()

  for (let index = 0; index < profile.numOrgs; index += 1) {
    const name = faker.company.name()
    const baseSlug = slugify(name)
    let slug = baseSlug
    let suffix = 1
    while (seenOrgSlugs.has(slug)) {
      suffix += 1
      slug = `${baseSlug}-${suffix}`
    }
    seenOrgSlugs.add(slug)
    let ownerEmail = faker.internet.email().toLowerCase()
    while (seenOrgEmails.has(ownerEmail)) {
      ownerEmail = faker.internet.email().toLowerCase()
    }
    seenOrgEmails.add(ownerEmail)
    organizations.push({
      id: deterministicUuid(),
      name,
      slug,
      plan: pickPlan(chance),
      region: pickRegion(chance),
      created_at: toIso(pastDate()),
      owner_email: ownerEmail
    })
  }

  for (let index = 0; index < profile.numUsers; index += 1) {
    const locale = pickLocale(chance)
    const edgeCase = withEdgeCase(
      chance,
      0.05,
      () => true,
      () => false
    )
    let email = edgeCase ? longEmail(index, locale) : faker.internet.email().toLowerCase()
    while (seenUserEmails.has(email)) {
      email = faker.internet.email().toLowerCase()
    }
    seenUserEmails.add(email)
    users.push({
      id: deterministicUuid(),
      email,
      full_name: edgeCase ? EDGE_CASE_NAMES[index % EDGE_CASE_NAMES.length]! : faker.person.fullName(),
      locale,
      timezone: edgeCase ? "UTC" : TIMEZONE_BY_LOCALE[locale],
      created_at: toIso(pastDate())
    })
  }

  for (const organization of organizations) {
    const count = memberCount(chance, users.length)
    const memberRows = chance.pickset(users, count)
    memberRows.forEach((user, index) => {
      memberships.push({
        id: deterministicUuid(),
        org_id: organization.id,
        user_id: user.id,
        role: index === 0 ? "owner" : pickMembershipRole(chance),
        joined_at: toIso(between(new Date(organization.created_at), BASE_TIME)),
        invited_by: index === 0 ? null : memberRows[chance.integer({ min: 0, max: index - 1 })]!.id
      })
    })
  }

  const datasetForPools: Dataset = {
    profileName: profile.name,
    seed: profile.seed,
    organizations,
    users,
    memberships,
    projects,
    auditEvents,
    apiKeys,
    invitations
  }
  const initialPools = buildPools(datasetForPools)

  for (const organization of organizations) {
    const memberIds = initialPools.orgMemberMap.get(organization.id) ?? []
    for (let index = 0; index < projectCount(chance); index += 1) {
      projects.push({
        id: deterministicUuid(),
        org_id: organization.id,
        name: faker.commerce.productName(),
        status: pickProjectStatus(chance),
        created_by: chance.pickone(memberIds),
        created_at: toIso(between(new Date(organization.created_at), BASE_TIME))
      })
    }
  }

  const poolsAfterProjects = buildPools({ ...datasetForPools, projects })

  for (const organization of organizations) {
    const memberIds = poolsAfterProjects.orgMemberMap.get(organization.id) ?? []
    for (let index = 0; index < apiKeyCount(chance); index += 1) {
      let keyPrefix = `tc_${chance.string({ length: 8, pool: KEY_ALPHABET })}`
      while (seenPrefixes.has(keyPrefix)) {
        keyPrefix = `tc_${chance.string({ length: 8, pool: KEY_ALPHABET })}`
      }
      seenPrefixes.add(keyPrefix)
      const createdAt = between(new Date(organization.created_at), BASE_TIME)
      apiKeys.push({
        id: deterministicUuid(),
        org_id: organization.id,
        created_by: chance.pickone(memberIds),
        name: faker.company.catchPhrase(),
        key_prefix: keyPrefix,
        created_at: toIso(createdAt),
        last_used_at: chance.bool({ likelihood: 70 }) ? toIso(between(createdAt, BASE_TIME)) : null
      })
    }
    const memberEmails = new Set((memberIds ?? []).map((memberId) => users.find((row) => row.id === memberId)!.email.toLowerCase()))
    for (let index = 0; index < invitationCount(chance); index += 1) {
      let invitedEmail = faker.internet.email().toLowerCase()
      while (memberEmails.has(invitedEmail)) {
        invitedEmail = faker.internet.email().toLowerCase()
      }
      invitations.push({
        id: deterministicUuid(),
        org_id: organization.id,
        invited_email: invitedEmail,
        role: pickInvitationRole(chance),
        invited_by: chance.pickone(memberIds),
        expires_at: toIso(futureDate()),
        accepted_at: chance.bool({ likelihood: 40 }) ? toIso(addDays(BASE_TIME, -chance.integer({ min: 1, max: 180 }))) : null
      })
    }
  }

  const pools = buildPools({
    ...datasetForPools,
    projects,
    apiKeys,
    invitations
  })
  for (const project of projects) {
    const memberIds = pools.orgMemberMap.get(project.org_id) ?? []
    const projectMemberships = pools.membershipsByOrg.get(project.org_id) ?? []
    const orgApiKeys = pools.apiKeysByOrg.get(project.org_id) ?? []
    const orgInvitations = pools.invitationsByOrg.get(project.org_id) ?? []
    for (let index = 0; index < auditEventCount(chance, project.status); index += 1) {
      const userId = chance.pickone(memberIds)
      const membership = pools.membershipByOrgUser.get(`${project.org_id}:${userId}`)!
      const floor = new Date(Math.max(new Date(project.created_at).getTime(), new Date(membership.joined_at).getTime()))
      const resourceType = chance.weighted(
        ["project", "user", "membership", "api_key", "invitation"],
        [35, 15, 25, 10, 15]
      ) as AuditEvent["resource_type"]
      const resourceCandidates: string[] =
        resourceType === "project"
          ? [project.id]
          : resourceType === "user"
            ? memberIds
            : resourceType === "membership"
              ? projectMemberships.map((row) => row.id)
              : resourceType === "api_key"
                ? orgApiKeys.map((row) => row.id)
                : orgInvitations.map((row) => row.id)
      const eventTs = between(floor, BASE_TIME)
      auditEvents.push({
        id: deterministicUuid(),
        org_id: project.org_id,
        user_id: userId,
        project_id: project.id,
        action: pickAuditAction(chance),
        resource_type: resourceCandidates.length > 0 ? resourceType : "project",
        resource_id: resourceCandidates.length > 0 ? chance.pickone(resourceCandidates) : project.id,
        ts: toIso(eventTs)
      })
    }
  }

  return {
    profileName: profile.name,
    seed: profile.seed,
    organizations,
    users,
    memberships,
    projects,
    auditEvents: sortAuditEvents(auditEvents),
    apiKeys,
    invitations
  }
}

export async function generateAndWrite(profile: Profile, format: "jsonl" | "csv", outputDir: string) {
  const dataset = await generateDataset(profile)
  const report = validateDataset(dataset)
  if (!report.ok) {
    throw new Error(`dataset failed validation: ${report.violations.join("; ")}`)
  }
  if (format === "jsonl") {
    await writeJsonl(dataset, outputDir, report)
  } else {
    await writeCsv(dataset, outputDir, report)
  }
  return { dataset, report }
}
