# Add Include/Exclude Filtering

## Purpose

Introduce explicit multi-select include and exclude filter semantics.

## When To Use It

- users need positive and negative selection in the same filter surface
- query params or form state currently blur include versus exclude intent

## Sequence

1. choose explicit parameter names such as `field_in` and `field_out`
2. normalize ordering, deduplication, and conflict resolution
3. implement the filtered query with named include and exclude steps
4. expose the normalized state in fragments or JSON payloads
5. verify representative include, exclude, and mixed cases

## Outputs

- normalized include/exclude state model
- endpoint or service logic for mixed filters
- verification of deterministic query behavior

## Related Doctrine

- `context/doctrine/filter-state-and-query-state.md`
- `context/doctrine/faceted-query-count-discipline.md`

## Common Pitfalls

- one ambiguous param that sometimes means include and sometimes exclude
- conflicting values resolved differently across endpoints
- counts that ignore excludes

## Stop Conditions

- include and exclude semantics are explicit in code and response state
- mixed-filter behavior is verified with exact expected rows or counts
