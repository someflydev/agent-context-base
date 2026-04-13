import type { Dataset, ValidationReport } from "./domain.js"
import {
  apiKeyIds,
  BASE_TIME,
  buildPools,
  fromIso,
  invitationIds,
  membershipIds,
  organizationById,
  userById
} from "./pools.js"

export function validateDataset(dataset: Dataset): ValidationReport {
  const violations: string[] = []
  const counts: Record<string, number> = {
    organizations: dataset.organizations.length,
    users: dataset.users.length,
    memberships: dataset.memberships.length,
    projects: dataset.projects.length,
    audit_events: dataset.auditEvents.length,
    api_keys: dataset.apiKeys.length,
    invitations: dataset.invitations.length
  }
  const minimumRows: Record<string, number> = {
    organizations: 1,
    users: 1,
    memberships: 1,
    projects: 1,
    audit_events: 1,
    api_keys: 0,
    invitations: 0
  }
  for (const [entity, count] of Object.entries(counts)) {
    if (count < minimumRows[entity]!) {
      violations.push(`row count below minimum for ${entity}: ${count} < ${minimumRows[entity]}`)
    }
  }

  const orgs = organizationById(dataset.organizations)
  const users = userById(dataset.users)
  const pools = buildPools(dataset)
  const projectIds = new Set(dataset.projects.map((row) => row.id))
  const membershipIdSet = membershipIds(dataset.memberships)
  const apiKeyIdSet = apiKeyIds(dataset.apiKeys)
  const invitationIdSet = invitationIds(dataset.invitations)

  const seenOrgIds = new Set<string>()
  const seenEmails = new Set<string>()
  const seenPrefixes = new Set<string>()
  const memberEmails = new Map<string, Set<string>>()

  for (const org of dataset.organizations) {
    if (seenOrgIds.has(org.id)) {
      violations.push(`duplicate organizations.id: ${org.id}`)
    }
    seenOrgIds.add(org.id)
  }
  for (const user of dataset.users) {
    const email = user.email.toLowerCase()
    if (seenEmails.has(email)) {
      violations.push(`duplicate user.email: ${email}`)
    }
    seenEmails.add(email)
  }
  for (const membership of dataset.memberships) {
    const org = orgs.get(membership.org_id)
    const user = users.get(membership.user_id)
    if (!org) {
      violations.push(`membership missing org: ${membership.id}`)
      continue
    }
    if (!user) {
      violations.push(`membership missing user: ${membership.id}`)
      continue
    }
    const emails = memberEmails.get(membership.org_id) ?? new Set<string>()
    emails.add(user.email.toLowerCase())
    memberEmails.set(membership.org_id, emails)
    if (fromIso(membership.joined_at) < fromIso(org.created_at)) {
      violations.push(`Rule A violated by membership ${membership.id}`)
    }
    if (membership.invited_by !== null && !users.has(membership.invited_by)) {
      violations.push(`membership invited_by missing user: ${membership.id}`)
    }
  }
  for (const project of dataset.projects) {
    const org = orgs.get(project.org_id)
    if (!org) {
      violations.push(`project missing org: ${project.id}`)
      continue
    }
    if (fromIso(project.created_at) < fromIso(org.created_at)) {
      violations.push(`Rule B violated by project ${project.id}`)
    }
    if (!(pools.orgMemberMap.get(project.org_id) ?? []).includes(project.created_by)) {
      violations.push(`Rule C violated by project ${project.id}`)
    }
  }
  for (const event of dataset.auditEvents) {
    const org = orgs.get(event.org_id)
    const project = pools.projectById.get(event.project_id)
    if (!org) {
      violations.push(`audit event missing org: ${event.id}`)
      continue
    }
    if (!project) {
      violations.push(`audit event missing project: ${event.id}`)
      continue
    }
    if (!(pools.orgMemberMap.get(event.org_id) ?? []).includes(event.user_id)) {
      violations.push(`Rule D violated by audit event ${event.id}`)
    }
    if (project.org_id !== event.org_id) {
      violations.push(`Rule E violated by audit event ${event.id}`)
    }
    const eventTs = fromIso(event.ts)
    if (eventTs < fromIso(project.created_at)) {
      violations.push(`Rule F violated by audit event ${event.id}`)
    }
    const membership = pools.membershipByOrgUser.get(`${event.org_id}:${event.user_id}`)
    if (membership && eventTs < fromIso(membership.joined_at)) {
      violations.push(`audit event before membership joined_at: ${event.id}`)
    }
    if (event.resource_type === "project" && !projectIds.has(event.resource_id)) {
      violations.push(`audit event resource project missing: ${event.id}`)
    }
    if (event.resource_type === "user" && !users.has(event.resource_id)) {
      violations.push(`audit event resource user missing: ${event.id}`)
    }
    if (event.resource_type === "membership" && !membershipIdSet.has(event.resource_id)) {
      violations.push(`audit event resource membership missing: ${event.id}`)
    }
    if (event.resource_type === "api_key" && !apiKeyIdSet.has(event.resource_id)) {
      violations.push(`audit event resource api_key missing: ${event.id}`)
    }
    if (event.resource_type === "invitation" && !invitationIdSet.has(event.resource_id)) {
      violations.push(`audit event resource invitation missing: ${event.id}`)
    }
  }
  for (const apiKey of dataset.apiKeys) {
    if (!(pools.orgMemberMap.get(apiKey.org_id) ?? []).includes(apiKey.created_by)) {
      violations.push(`Rule G violated by api_key ${apiKey.id}`)
    }
    if (seenPrefixes.has(apiKey.key_prefix)) {
      violations.push(`duplicate api_key.key_prefix: ${apiKey.key_prefix}`)
    }
    seenPrefixes.add(apiKey.key_prefix)
    if (apiKey.last_used_at !== null && fromIso(apiKey.last_used_at) < fromIso(apiKey.created_at)) {
      violations.push(`api_key last_used_at before created_at: ${apiKey.id}`)
    }
  }
  for (const invitation of dataset.invitations) {
    if (!(pools.orgMemberMap.get(invitation.org_id) ?? []).includes(invitation.invited_by)) {
      violations.push(`Rule H violated by invitation ${invitation.id}`)
    }
    if ((memberEmails.get(invitation.org_id) ?? new Set<string>()).has(invitation.invited_email.toLowerCase())) {
      violations.push(`Rule I violated by invitation ${invitation.id}`)
    }
    if (fromIso(invitation.expires_at) <= BASE_TIME) {
      violations.push(`invitation expiry must be in the future: ${invitation.id}`)
    }
    if (invitation.accepted_at !== null && fromIso(invitation.accepted_at) > BASE_TIME) {
      violations.push(`invitation accepted_at must be in the past: ${invitation.id}`)
    }
  }

  return {
    ok: violations.length === 0,
    violations,
    counts,
    seed: dataset.seed,
    profileName: dataset.profileName
  }
}
