export interface Organization {
  id: string
  name: string
  slug: string
  plan: "free" | "pro" | "enterprise"
  region: "us-east" | "us-west" | "eu-west" | "ap-southeast"
  created_at: string
  owner_email: string
}

export interface User {
  id: string
  email: string
  full_name: string
  locale: "en-US" | "en-GB" | "de-DE" | "fr-FR"
  timezone: string
  created_at: string
}

export interface Membership {
  id: string
  org_id: string
  user_id: string
  role: "owner" | "admin" | "member" | "viewer"
  joined_at: string
  invited_by: string | null
}

export interface Project {
  id: string
  org_id: string
  name: string
  status: "active" | "archived" | "draft"
  created_by: string
  created_at: string
}

export interface AuditEvent {
  id: string
  org_id: string
  user_id: string
  project_id: string
  action: "created" | "updated" | "deleted" | "archived" | "invited" | "exported"
  resource_type: "project" | "user" | "membership" | "api_key" | "invitation"
  resource_id: string
  ts: string
}

export interface ApiKey {
  id: string
  org_id: string
  created_by: string
  name: string
  key_prefix: string
  created_at: string
  last_used_at: string | null
}

export interface Invitation {
  id: string
  org_id: string
  invited_email: string
  role: "admin" | "member" | "viewer"
  invited_by: string
  expires_at: string
  accepted_at: string | null
}

export interface Dataset {
  profileName: string
  seed: number
  organizations: Organization[]
  users: User[]
  memberships: Membership[]
  projects: Project[]
  auditEvents: AuditEvent[]
  apiKeys: ApiKey[]
  invitations: Invitation[]
}

export interface ValidationReport {
  ok: boolean
  violations: string[]
  counts: Record<string, number>
  seed: number
  profileName: string
}
