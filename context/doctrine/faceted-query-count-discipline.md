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

## Verification Targets

- result count matches the actual filtered rows
- option counts match the documented facet semantics
- excluded values do not silently contribute to available counts
- empty-result states and zero-count options render clearly
