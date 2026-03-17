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

Filter panel fragments must additionally expose include/exclude visual state on every option element:

- `data-excluded="true"` on any include option whose value is in the active D_out (greyed, disabled)
- `data-active="true"` on any exclude option whose value is in the active D_out (checked, highlighted)
- `data-option-count` must reflect the correct count for the option's mode (0 for excluded include options; exclude impact count for exclude options)

Omitting these markers makes the fragment unverifiable. Playwright assertions and backend unit tests rely on them as the verification contract.

## Synchronization Rule

HTMX forms, hidden inputs, pagination links, count fragments, and chart endpoints must all carry the same normalized state.

If the result list updates but the filter panel or chart uses stale params, the interface is incorrect even if each endpoint works in isolation.

## Extended State Fields (PROMPT_64)

Two new fields are now canonical parts of the query state model:

**`query`** — string, default `""` (empty string).
- Query parameter name: `query` (single value, not multi-value).
- Normalize: trim whitespace; lowercase. Empty after trimming → treat as absent.
- Applied as a base filter before any facet dimension logic. Never relaxed.
- Included in the fingerprint: `|query={Q}`.
- Reflected in `data-search-query="{Q}"` on the results section element and on the
  search input element itself.

**`sort`** — string, default `"events_desc"`.
- Query parameter name: `sort` (single value, not multi-value).
- Valid values: `events_desc`, `events_asc`, `name_asc`. Unrecognised values default to `events_desc`.
- Affects result display order only. Sort never affects any count of any kind.
- Included in the fingerprint: `|sort={sort}`.
- Reflected in `data-sort-order="{sort}"` on the results section element and on the
  sort select element.

Both fields must be preserved across HTMX partial swaps. If the results fragment is
re-rendered without restoring `query` and `sort` from state, the search input clears and
the sort dropdown resets on every filter change.

## Common Mistakes

- mutating filter state in template code instead of a named parser
- sorting selected values differently across endpoints
- dropping excludes when generating chart requests
- rendering count fragments without the state they summarize
- applying `sort` to count computations (sort never affects counts)
- computing facet counts against the pre-search row set when Q is active
- omitting `query` or `sort` from the fingerprint string
