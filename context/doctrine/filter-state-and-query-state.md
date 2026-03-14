# Filter State And Query State

Interactive filtering stays reliable when UI state and backend query state are treated as one contract.

## State Model

Use one normalized query-state structure with:

- one field per facet dimension
- explicit include and exclude collections
- deterministic ordering
- a stable fingerprint or serialized form for comparison and caching

## Naming Rule

Prefer explicit names such as:

- `status_in`
- `status_out`
- `team_in`
- `team_out`

Do not overload one field to mean both inclusion and exclusion.

## Fragment Rule

Every backend-generated fragment that depends on query state should expose enough state to debug and verify:

- active result count
- active filters
- stable `data-*` markers or ids
- optional query fingerprint

## Synchronization Rule

HTMX forms, hidden inputs, pagination links, count fragments, and chart endpoints must all carry the same normalized state.

If the result list updates but the filter panel or chart uses stale params, the interface is incorrect even if each endpoint works in isolation.

## Common Mistakes

- mutating filter state in template code instead of a named parser
- sorting selected values differently across endpoints
- dropping excludes when generating chart requests
- rendering count fragments without the state they summarize
