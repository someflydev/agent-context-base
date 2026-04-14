package io.agentcontextbase.faker

case class Organization(
  id: String,
  name: String,
  slug: String,
  plan: String,
  region: String,
  created_at: String,
  owner_email: String
)

case class User(
  id: String,
  email: String,
  full_name: String,
  locale: String,
  timezone: String,
  created_at: String
)

case class Membership(
  id: String,
  org_id: String,
  user_id: String,
  role: String,
  joined_at: String,
  invited_by: String // Can be null (or Option, but keeping simple as String, using null or empty for none)
)

case class Project(
  id: String,
  org_id: String,
  name: String,
  status: String,
  created_by: String,
  created_at: String
)

case class AuditEvent(
  id: String,
  org_id: String,
  user_id: String,
  project_id: String,
  action: String,
  resource_type: String,
  resource_id: String,
  ts: String
)

case class ApiKey(
  id: String,
  org_id: String,
  created_by: String,
  name: String,
  key_prefix: String,
  created_at: String,
  last_used_at: String
)

case class Invitation(
  id: String,
  org_id: String,
  invited_email: String,
  role: String,
  invited_by: String,
  expires_at: String,
  accepted_at: String
)

case class Dataset(
  organizations: Vector[Organization],
  users: Vector[User],
  memberships: Vector[Membership],
  projects: Vector[Project],
  audit_events: Vector[AuditEvent],
  api_keys: Vector[ApiKey],
  invitations: Vector[Invitation],
  report: Option[ValidationReport] = None
)

case class ValidationReport(
  ok: Boolean,
  violations: Vector[String],
  counts: Map[String, Int],
  seed: Long,
  profileName: String
)
