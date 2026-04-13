import type Chance from "chance"
import { clamp } from "./pools.js"

const PLAN_VALUES = ["free", "pro", "enterprise"] as const
const REGION_VALUES = ["us-east", "us-west", "eu-west", "ap-southeast"] as const
const ROLE_VALUES = ["owner", "admin", "member", "viewer"] as const
const PROJECT_STATUS_VALUES = ["active", "archived", "draft"] as const
const AUDIT_ACTION_VALUES = ["updated", "created", "exported", "invited", "archived", "deleted"] as const
const RESOURCE_TYPE_VALUES = ["project", "user", "membership", "api_key", "invitation"] as const
const INVITATION_ROLE_VALUES = ["admin", "member", "viewer"] as const
const LOCALE_VALUES = ["en-US", "en-GB", "de-DE", "fr-FR"] as const

export function pickPlan(c: Chance.Chance): (typeof PLAN_VALUES)[number] {
  return c.weighted([...PLAN_VALUES], [50, 35, 15])
}

export function pickRegion(c: Chance.Chance): (typeof REGION_VALUES)[number] {
  return c.weighted([...REGION_VALUES], [40, 25, 20, 15])
}

export function pickLocale(c: Chance.Chance): (typeof LOCALE_VALUES)[number] {
  return c.weighted([...LOCALE_VALUES], [60, 20, 10, 10])
}

export function pickMembershipRole(c: Chance.Chance): (typeof ROLE_VALUES)[number] {
  return c.weighted([...ROLE_VALUES], [5, 10, 60, 25])
}

export function pickProjectStatus(c: Chance.Chance): (typeof PROJECT_STATUS_VALUES)[number] {
  return c.weighted([...PROJECT_STATUS_VALUES], [60, 25, 15])
}

export function pickAuditAction(c: Chance.Chance): (typeof AUDIT_ACTION_VALUES)[number] {
  return c.weighted([...AUDIT_ACTION_VALUES], [35, 20, 15, 12, 10, 8])
}

export function pickResourceType(c: Chance.Chance): (typeof RESOURCE_TYPE_VALUES)[number] {
  return c.weighted([...RESOURCE_TYPE_VALUES], [35, 15, 25, 10, 15])
}

export function pickInvitationRole(c: Chance.Chance): (typeof INVITATION_ROLE_VALUES)[number] {
  return c.weighted([...INVITATION_ROLE_VALUES], [15, 65, 20])
}

export function memberCount(c: Chance.Chance, maxUsers: number): number {
  // Chance exposes rpg(), normal(), and boolean helpers that make shaped
  // distributions clearer than uniform sampling for small teaching examples.
  const poissonLike = c.normal({ mean: 4, dev: 2 })
  const shaped = Math.round(poissonLike + (c.rpg("1d3", { sum: true }) as number))
  return clamp(shaped + 1, 3, Math.min(50, maxUsers))
}

export function projectCount(c: Chance.Chance): number {
  return clamp(Math.round(c.normal({ mean: 3.5, dev: 2.2 })), 1, 20)
}

export function apiKeyCount(c: Chance.Chance): number {
  return clamp(Math.round(c.normal({ mean: 2, dev: 2 })), 0, 10)
}

export function invitationCount(c: Chance.Chance): number {
  return clamp(Math.round(c.normal({ mean: 1.5, dev: 1.2 })), 0, 5)
}

export function auditEventCount(c: Chance.Chance, status: "active" | "archived" | "draft"): number {
  if (status === "active") {
    return clamp(Math.round(c.normal({ mean: 14, dev: 5 })), 8, 30)
  }
  if (status === "archived") {
    return clamp(Math.round(c.normal({ mean: 8, dev: 3 })), 4, 18)
  }
  return clamp(Math.round(c.normal({ mean: 4, dev: 2 })), 2, 10)
}

export function withEdgeCase<T>(c: Chance.Chance, rate: number, edgeFn: () => T, normalFn: () => T): T {
  return c.bool({ likelihood: rate * 100 }) ? edgeFn() : normalFn()
}
