# Faceted Query Count Discipline

Facet counts are only useful when they reflect the real query semantics.

## Result Count Rule

The visible result count must equal the number of rows returned by the active backend query after all include and exclude filters are applied.

Do not compute the badge, table, and pagination count from separate approximations.

## Option Count Rule

Per-option counts should be computed with all filters applied except include selections for the current facet dimension.

That means:

- keep filters from other dimensions active
- keep excludes for the current dimension explicit
- do not reuse stale totals from a previous request

## Include And Exclude Semantics

- include selections narrow the dataset to rows matching any selected value within that dimension
- exclude selections remove rows matching any selected value within that dimension
- if a value appears in both include and exclude sets, the backend should resolve it explicitly and deterministically

## Query Discipline

- name the base query and the facet-count query separately
- keep them in the same service or query module
- document whether counts are computed before or after same-dimension includes are relaxed
- expose the active filter state in the fragment or payload so verification can compare state to counts

## Include/Exclude Visual State Rules

When a value V is in a dimension's exclude set (D_out):

- The INCLUDE option for V must show count 0. Computing a non-zero include count for an excluded value implies the user could add it to the include set while it is excluded. That is misleading.
- The INCLUDE option must be visually greyed out and its checkbox disabled (`opacity-50 cursor-not-allowed`, `disabled` attribute, `data-excluded="true"`).
- The EXCLUDE option for V must NOT be greyed out. It is the active filter and shows a meaningful count.
- The INCLUDE option must not be hidden. The user should see it exists and understand why it is unavailable.

These rules apply regardless of stack or template system.

## Exclude Impact Count

The count shown on an exclude option for value V in dimension D answers: "How many rows does this exclusion remove from the current result set?"

Computation (`exclude_impact_counts(state, dimension)`):

1. Apply all active filters for all OTHER dimensions fully (both _in and _out).
2. Apply all active excludes for dimension D EXCEPT the specific value V being counted.
3. Do NOT apply any includes for dimension D.
4. Count rows where row[D] == V.

This is a distinct computation from the normal include-count/facet-count path. Name it explicitly in code. When no excludes are active for D, this function still returns a useful preview count: how many rows the option would remove if excluded.

Do not derive the exclude impact count from the facet_counts path. That path relaxes the dimension's own includes, not its excludes, and will produce incorrect results for this purpose.

## Verification Targets

- result count matches the actual filtered rows
- option counts match the documented facet semantics
- excluded values do not silently contribute to available counts
- empty-result states and zero-count options render clearly
- include option for an excluded value has count 0 and data-excluded="true"
- exclude option for an excluded value has a non-zero impact count and data-active="true"

## Text Search as Base Filter

Text search (the `query` parameter) is a **base filter**: it is applied before any facet
dimension logic runs. It is never relaxed by the same-dimension relaxation that
`facet_counts` applies to includes.

### Application order

1. Apply Q (case-insensitive substring match on `report_id` at minimum) to the full
   row set. The narrowed set is the new working set for all subsequent computations.
2. Apply dimension filters (_in, _out) to the narrowed set.

This ordering applies identically to `filter_rows`, `facet_counts`, and
`exclude_impact_counts`.

### Count semantics when Q is active

- `facet_counts(state, dimension)` must call `apply_text_search` first, then apply other
  dimensions, then relax same-dimension includes. Q is never relaxed.
- `exclude_impact_counts(state, dimension)` must call `apply_text_search` first, then
  apply other dimensions (no relaxation), then count by option value.
- The result-count badge always reflects rows passing both Q and all facet filters.
- Facet option counts reflect the search-narrowed working set. Showing pre-search counts
  when Q is active is a correctness failure: option counts would claim more rows than
  exist in the visible result set.

### When Q is empty

All existing count semantics apply unchanged. There is no behaviour difference between
an absent `query` parameter and an empty string after trimming.

### Correctness failure pattern

Computing facet option counts against the full dataset when Q is active produces counts
that are larger than the result set can satisfy. A user who sees "platform: 3" in the
team facet but only 1 visible result will correctly distrust the interface.

Do not cache pre-search counts and display them during an active search. Always recompute
counts against the search-narrowed working set.

### Related

- `context/doctrine/search-sort-scroll-layout.md` — full RULE 4 specification
- `context/workflows/add-text-search-to-filter-ui.md`
