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
6. render split include/exclude options per dimension group:
   - Apply RULE 1: if value is in D_out, set include option count to 0, add
     `disabled` to the checkbox, add `data-excluded="true"`, apply
     `opacity-50 cursor-not-allowed` to the label
   - Apply RULE 2: compute `exclude_impact_counts(state, dimension)` separately
     from `facet_counts`; show the result on each exclude option
   - Carry all required `data-*` attributes on every include and exclude option
   - See `context/doctrine/filter-panel-rendering-rules.md` for the full contract

## Outputs

- normalized include/exclude state model
- endpoint or service logic for mixed filters
- verification of deterministic query behavior
- split include/exclude filter panel fragment with correct visual state

## Related Doctrine

- `context/doctrine/filter-state-and-query-state.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/filter-panel-rendering-rules.md`

## Common Pitfalls

- one ambiguous param that sometimes means include and sometimes exclude
- conflicting values resolved differently across endpoints
- counts that ignore excludes

## Stop Conditions

- include and exclude semantics are explicit in code and response state
- mixed-filter behavior is verified with exact expected rows or counts
