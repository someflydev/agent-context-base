import { mkdir, writeFile } from "node:fs/promises"
import { join } from "node:path"
import type { ApiKey, AuditEvent, Dataset, Invitation, Membership, Organization, Project, User } from "./domain.js"

export const BASE_TIME = new Date("2026-01-01T12:00:00.000Z")
export const TIMEZONE_BY_LOCALE: Record<string, string> = {
  "en-US": "America/New_York",
  "en-GB": "Europe/London",
  "de-DE": "Europe/Berlin",
  "fr-FR": "Europe/Paris"
}

export interface GenerationPools {
  orgMemberMap: Map<string, string[]>
  userEmailById: Map<string, string>
  projectById: Map<string, Project>
  projectsByOrg: Map<string, Project[]>
  membershipsByOrg: Map<string, Membership[]>
  membershipByOrgUser: Map<string, Membership>
  apiKeysByOrg: Map<string, ApiKey[]>
  invitationsByOrg: Map<string, Invitation[]>
}

export function toIso(value: Date): string {
  return new Date(value.getTime()).toISOString().replace(".000Z", "Z")
}

export function fromIso(value: string): Date {
  return new Date(value)
}

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "tenantcore"
}

export function clamp(value: number, minimum: number, maximum: number): number {
  return Math.max(minimum, Math.min(maximum, value))
}

export function addDays(date: Date, days: number, seconds = 0): Date {
  return new Date(date.getTime() + (days * 86400 + seconds) * 1000)
}

export function buildPools(dataset: Dataset): GenerationPools {
  const orgMemberMap = new Map<string, string[]>()
  const userEmailById = new Map<string, string>()
  const projectById = new Map<string, Project>()
  const projectsByOrg = new Map<string, Project[]>()
  const membershipsByOrg = new Map<string, Membership[]>()
  const membershipByOrgUser = new Map<string, Membership>()
  const apiKeysByOrg = new Map<string, ApiKey[]>()
  const invitationsByOrg = new Map<string, Invitation[]>()

  for (const user of dataset.users) {
    userEmailById.set(user.id, user.email.toLowerCase())
  }
  for (const membership of dataset.memberships) {
    const memberIds = orgMemberMap.get(membership.org_id) ?? []
    memberIds.push(membership.user_id)
    orgMemberMap.set(membership.org_id, memberIds)
    const membershipRows = membershipsByOrg.get(membership.org_id) ?? []
    membershipRows.push(membership)
    membershipsByOrg.set(membership.org_id, membershipRows)
    membershipByOrgUser.set(`${membership.org_id}:${membership.user_id}`, membership)
  }
  for (const project of dataset.projects) {
    projectById.set(project.id, project)
    const projectRows = projectsByOrg.get(project.org_id) ?? []
    projectRows.push(project)
    projectsByOrg.set(project.org_id, projectRows)
  }
  for (const apiKey of dataset.apiKeys) {
    const rows = apiKeysByOrg.get(apiKey.org_id) ?? []
    rows.push(apiKey)
    apiKeysByOrg.set(apiKey.org_id, rows)
  }
  for (const invitation of dataset.invitations) {
    const rows = invitationsByOrg.get(invitation.org_id) ?? []
    rows.push(invitation)
    invitationsByOrg.set(invitation.org_id, rows)
  }

  return {
    orgMemberMap,
    userEmailById,
    projectById,
    projectsByOrg,
    membershipsByOrg,
    membershipByOrgUser,
    apiKeysByOrg,
    invitationsByOrg
  }
}

export async function writeJsonl(dataset: Dataset, outputDir: string, report: object): Promise<void> {
  await mkdir(outputDir, { recursive: true })
  const entities: Array<[string, object[]]> = [
    ["organizations", dataset.organizations],
    ["users", dataset.users],
    ["memberships", dataset.memberships],
    ["projects", dataset.projects],
    ["audit_events", dataset.auditEvents],
    ["api_keys", dataset.apiKeys],
    ["invitations", dataset.invitations]
  ]
  for (const [name, rows] of entities) {
    const body = rows.map((row) => JSON.stringify(row)).join("\n")
    await writeFile(join(outputDir, `${name}.jsonl`), `${body}${body ? "\n" : ""}`, "utf8")
  }
  await writeFile(join(outputDir, `${dataset.profileName}-report.json`), JSON.stringify(report, null, 2), "utf8")
}

export async function writeCsv(dataset: Dataset, outputDir: string, report: { counts: Record<string, number>; ok: boolean; seed: number; profileName: string }): Promise<void> {
  await mkdir(outputDir, { recursive: true })
  const entities: Array<[string, object[]]> = [
    ["organizations", dataset.organizations],
    ["users", dataset.users],
    ["memberships", dataset.memberships],
    ["projects", dataset.projects],
    ["audit_events", dataset.auditEvents],
    ["api_keys", dataset.apiKeys],
    ["invitations", dataset.invitations]
  ]
  for (const [name, rows] of entities) {
    if (rows.length === 0) {
      await writeFile(join(outputDir, `${name}.csv`), "", "utf8")
      continue
    }
    const keys = Object.keys(rows[0]!)
    const lines = [
      keys.join(","),
      ...rows.map((row) =>
        keys
          .map((key) => JSON.stringify((row as Record<string, unknown>)[key] ?? ""))
          .join(",")
      )
    ]
    await writeFile(join(outputDir, `${name}.csv`), `${lines.join("\n")}\n`, "utf8")
  }
  const reportLines = [
    "profile,seed,ok,entity,count",
    ...Object.entries(report.counts).map(([entity, count]) => `${report.profileName},${report.seed},${report.ok},${entity},${count}`)
  ]
  await writeFile(join(outputDir, `${dataset.profileName}-report.csv`), `${reportLines.join("\n")}\n`, "utf8")
}

export function organizationById(organizations: Organization[]): Map<string, Organization> {
  return new Map(organizations.map((row) => [row.id, row]))
}

export function userById(users: User[]): Map<string, User> {
  return new Map(users.map((row) => [row.id, row]))
}

export function membershipIds(memberships: Membership[]): Set<string> {
  return new Set(memberships.map((row) => row.id))
}

export function apiKeyIds(apiKeys: ApiKey[]): Set<string> {
  return new Set(apiKeys.map((row) => row.id))
}

export function invitationIds(invitations: Invitation[]): Set<string> {
  return new Set(invitations.map((row) => row.id))
}

export function sortAuditEvents(events: AuditEvent[]): AuditEvent[] {
  return [...events].sort((left, right) => left.ts.localeCompare(right.ts))
}
