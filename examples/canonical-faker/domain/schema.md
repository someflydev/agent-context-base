# TenantCore Domain Specification

## Domain Identity

TenantCore is a fictional SaaS multi-tenant platform used exclusively for
generating canonical synthetic datasets in `agent-context-base`. It is not a
real product. All generated data is synthetic.

## Entity Graph

```text
organizations
    |
    +-- users (via memberships)
    |       |
    |       +-- memberships (org_id + user_id + role)
    |
    +-- projects (org_id)
    |       |
    |       +-- audit_events (org_id + user_id + project_id)
    |
    +-- api_keys (org_id + created_by)
    |
    +-- invitations (org_id + invited_email + role)
```

## Entity Definitions

For each entity, the table below lists field name, type, constraints, and
generation notes.

### organizations

| Field | Type | Constraints | Generation Notes |
| --- | --- | --- | --- |
| id | UUID v4 | unique, primary key | Generate first; add to org ID pool |
| name | string | unique, non-empty | Faker company name |
| slug | string | unique, url-safe | Derived from name plus collision suffix |
| plan | enum | one of `free`, `pro`, `enterprise` | Weighted: 50% free, 35% pro, 15% enterprise |
| region | enum | one of `us-east`, `us-west`, `eu-west`, `ap-southeast` | Weighted by realistic distribution |
| created_at | timestamp | past 3 years | Faker past date within range |
| owner_email | string | unique, valid email | Faker email |

### users

| Field | Type | Constraints | Generation Notes |
| --- | --- | --- | --- |
| id | UUID v4 | unique, primary key | Generate after orgs; add to user ID pool |
| email | string | unique, valid email | Faker email; must be globally unique |
| full_name | string | non-empty | Faker full name |
| locale | string | BCP-47 code | Weighted: 60% `en-US`, others distributed |
| timezone | string | IANA tz name | Consistent with locale; not random |
| created_at | timestamp | past 3 years | May predate membership |

### memberships

| Field | Type | Constraints | Generation Notes |
| --- | --- | --- | --- |
| id | UUID v4 | unique, primary key | Generated after root pools exist |
| org_id | UUID v4 | FK -> `organizations.id` | Draw from org ID pool |
| user_id | UUID v4 | FK -> `users.id` | Draw from user ID pool |
| role | enum | one of `owner`, `admin`, `member`, `viewer` | Weighted: 5% owner, 10% admin, 60% member, 25% viewer |
| joined_at | timestamp | `>= organization.created_at` | Cannot predate the organization |
| invited_by | UUID v4 | FK -> `users.id` or null | Null for the first owner of an org |

Cardinality: 3-50 members per org. Skewed: most orgs have 3-10.

### projects

| Field | Type | Constraints | Generation Notes |
| --- | --- | --- | --- |
| id | UUID v4 | unique, primary key | Generated after memberships |
| org_id | UUID v4 | FK -> `organizations.id` | Draw from org ID pool |
| name | string | non-empty | Faker product or project label |
| status | enum | one of `active`, `archived`, `draft` | Weighted: 60% active, 25% archived, 15% draft |
| created_by | UUID v4 | FK -> `users.id`; must be member of `org_id` | Cross-field rule |
| created_at | timestamp | `>= organization.created_at` | Derived from org timeline |

Cardinality: 1-20 projects per org. Skewed: most orgs have 1-5.

### audit_events

| Field | Type | Constraints | Generation Notes |
| --- | --- | --- | --- |
| id | UUID v4 | unique, primary key | Generated after projects, `api_keys`, and `invitations` |
| org_id | UUID v4 | FK -> `organizations.id` | Must match project org |
| user_id | UUID v4 | FK -> `users.id`; must be member of `org_id` | Cross-field rule |
| project_id | UUID v4 | FK -> `projects.id`; must belong to `org_id` | Cross-field rule |
| action | string | one of `created`, `updated`, `deleted`, `archived`, `invited`, `exported` | Weighted by realistic activity mix |
| resource_type | string | one of `project`, `user`, `membership`, `api_key`, `invitation` | Action target kind |
| resource_id | UUID v4 | references a generated entity ID | Prefer same-org targets |
| ts | timestamp | `>= project.created_at` and `>= membership.joined_at` for `user_id` in `org_id` | Temporal rule |

Cardinality: 5-500 events per project. Skewed: active projects have more
events.

### api_keys

| Field | Type | Constraints | Generation Notes |
| --- | --- | --- | --- |
| id | UUID v4 | unique, primary key | Generated late because they depend on members |
| org_id | UUID v4 | FK -> `organizations.id` | Draw from org ID pool |
| created_by | UUID v4 | FK -> `users.id`; must be member of `org_id` | Cross-field rule |
| name | string | non-empty | Faker short phrase |
| key_prefix | string | unique, 8 chars after `tc_` prefix | `tc_` plus random alphanumeric |
| created_at | timestamp | `>= organization.created_at` | Derived from org timeline |
| last_used_at | timestamp | null or `>= created_at` | Optional access timestamp |

Cardinality: 0-10 `api_keys` per org.

### invitations

| Field | Type | Constraints | Generation Notes |
| --- | --- | --- | --- |
| id | UUID v4 | unique, primary key | Generated last |
| org_id | UUID v4 | FK -> `organizations.id` | Draw from org ID pool |
| invited_email | string | valid email | Must not match an existing member email |
| role | enum | one of `admin`, `member`, `viewer` | Invitation role target |
| invited_by | UUID v4 | FK -> `users.id`; must be member of `org_id` | Cross-field rule |
| expires_at | timestamp | `> now`, within 30 days | Future-facing invitation deadline |
| accepted_at | timestamp | null or past | 40% accepted, 60% pending |

Cardinality: 0-5 invitations per org, with pending invitations dominating.

## Cross-Field Rules

These rules are enforced in validation and must hold in every language
implementation.

- Rule A: `membership.joined_at >= organization.created_at`
- Rule B: `project.created_at >= organization.created_at`
- Rule C: `project.created_by` must be a member of `project.org_id`
- Rule D: `audit_event.user_id` must be a member of `audit_event.org_id`
- Rule E: `audit_event.project_id` must belong to `audit_event.org_id`
- Rule F: `audit_event.ts >= project.created_at` for that project
- Rule G: `api_key.created_by` must be a member of `api_key.org_id`
- Rule H: `invitation.invited_by` must be a member of `invitation.org_id`
- Rule I: `invitation.invited_email` must not match any member email for that
  org
