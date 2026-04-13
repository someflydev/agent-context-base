# TenantCore Generation Order

## Canonical Generation Sequence

The following order must be followed in every language implementation. It
satisfies all foreign key constraints and cross-field rules without retry
loops.

Stage 1 - Root entities (no parents):
1. Generate `organizations`
   -> Build org ID pool
   -> Build org metadata map (`plan`, `region`, `created_at`, `member_ids`)

Stage 2 - Global entities (reference orgs but are globally unique):
2. Generate `users`
   -> Build user ID pool
   -> Build user metadata map (`locale`, `timezone`, `email`)

Stage 3 - Bridge entities (join roots to global entities):
3. Generate `memberships` (`org_id x user_id x role x joined_at`)
   -> For each org: sample from the global user pool
   -> Apply cardinality rule: 3-50 members per org, skewed toward 3-10
   -> Build `org_member_map`: `org_id -> set[user_id]`

Stage 4 - Owned entities (require org plus member):
4. Generate `projects` (`org_id`, `created_by` from `org_member_map`)
   -> Build project ID pool
   -> Build project metadata map (`org_id`, `created_at`, `status`)

Stage 5 - Support entities (optional but referenceable by events):
5. Generate `api_keys` (`org_id`, `created_by` from `org_member_map`)
6. Generate `invitations` (`org_id`, `invited_by` from `org_member_map`,
   `invited_email` not already present in org member emails)

Stage 6 - Activity entities (require org plus member plus project, and may
reference support entities):
7. Generate `audit_events` (`org_id`, `user_id` from `org_member_map`,
   `project_id` from an org project, `resource_id` from an already-generated
   entity in the same org, `ts >= project.created_at`)

## ID Pool Pattern

Every stage must maintain an ID pool. Do not inline ID generation while
building dependent entities because later stages need a stable, already-built
lookup surface.

Python pseudocode (conceptual only):

```python
org_ids = []
organizations = []
for _ in range(profile.num_orgs):
    org = generate_org(seed_state)
    org_ids.append(org["id"])
    organizations.append(org)
```

## Why This Order Matters

Generating children before parents creates forward references that cannot be
resolved safely at generation time. That forces retry loops, hidden buffering,
or broken foreign keys when a missing parent never materializes. The canonical
order makes every foreign key and cross-field dependency, including
`audit_events.resource_id` references to `api_keys` or `invitations`,
resolvable on first write, which keeps the generator deterministic and
validation-friendly across all ten language implementations.
