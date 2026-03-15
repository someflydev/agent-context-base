# Filter Panel Rendering Rules

This is the authoritative rendering contract for include/exclude filter panels in
backend-driven HTMX UIs. It is stack-agnostic: Python/FastAPI, Elixir/Phoenix, and
any future stack must follow the same rules and emit the same data-* attributes.

## Structure: Split Include and Exclude per Dimension

Each dimension group in the filter panel must contain two distinct sub-sections:

1. **Include sub-section** — one labeled checkbox per option. Checked when the value
   is in D_in. Count badge shows the include/facet count (rows added if selected).
2. **Exclude sub-section** — one labeled checkbox per option. Checked when the value
   is in D_out. Count badge shows the exclude impact count (rows removed if active).

Do not merge include and exclude options into a single list or use a toggle/radio
pattern that conflates both modes. The user must be able to see both the include
and exclude state for every value simultaneously.

## Rule 1 — Include Option for an Excluded Value

When value V is in D_out:

- The include option for V MUST show `data-option-count="0"`. Do not run the normal
  facet_counts path for V and display whatever it returns. Short-circuit to 0.
- The include option MUST carry `data-excluded="true"`.
- The include option MUST be visually greyed: `opacity-50 cursor-not-allowed` (Tailwind)
  or equivalent CSS. Its checkbox MUST carry the `disabled` attribute.
- The include option MUST NOT be hidden. The user should see it exists.
- The exclude option for V MUST NOT be greyed. It is the active filter.

**Rationale:** A non-zero include count for an excluded value implies the user can
include it while excluding it. That is a trust failure, not a cosmetic one.

## Rule 2 — Exclude Impact Count

The count on an exclude option answers: "How many rows does this exclusion currently
remove?" Name the function `exclude_impact_counts(state, dimension)` in backend code.

Computation for value V in dimension D:

1. Apply all _in and _out for all OTHER dimensions fully.
2. Apply D_out EXCEPT V (other excludes in the same dimension).
3. Do NOT apply D_in at all.
4. Count rows where row[D] == V.

This is a new function, distinct from `facet_counts`. Do not reuse or wrap `facet_counts`
for this purpose — it relaxes includes, not excludes, and will return wrong values.

When no excludes are active, `exclude_impact_counts` still returns a useful preview
(how many rows would be removed if this value were excluded). Show it in the exclude
sub-section regardless of active state.

## Rule 3 — Quick Excludes Strip

The filter panel may include a quick-excludes strip at the top of the panel. When present:

### 3a — Declaration
Quick excludes must be declared as a backend constant, not auto-derived from the data.
```python
QUICK_EXCLUDES: list[tuple[str, str]] = [("status", "archived"), ("status", "paused")]
```

### 3b — Main Section Mirror
Every quick exclude value MUST also exist as an explicit exclude option in the
corresponding dimension group below. The strip is a convenience layer; it does not
replace the main filter section.

### 3c — Active State Synchronization
Quick exclude toggles and their corresponding main-section exclude options represent
the same filter state. Both must reflect whether the value is in D_out:

- When active (value in D_out): quick toggle is checked/highlighted, main exclude
  option checkbox is checked.
- When inactive: both are unchecked.

Use shared `name`/`value` form inputs so both submit the same filter state. The
backend re-renders both with consistent state on every request.

### 3d — Data Attributes on Quick Exclude Toggles
```
data-role="quick-exclude"
data-quick-exclude-dimension="<dimension>"
data-quick-exclude-value="<value>"
data-active="true" or data-active="false"
```

## Data-* Attribute Contract

All filter panel option elements must carry these attributes. They are the
verification contract for Playwright assertions and backend unit tests.

**Include option element:**
```
data-filter-dimension="<dimension>"
data-filter-option="<value>"
data-filter-mode="include"
data-option-count="<N>"       -- 0 when value is in D_out (Rule 1)
data-excluded="true"          -- present only when value is in D_out
```

**Exclude option element:**
```
data-filter-dimension="<dimension>"
data-filter-option="<value>"
data-filter-mode="exclude"
data-option-count="<N>"       -- exclude impact count (Rule 2), non-zero when active
data-active="true"            -- present when value is in D_out
```

**Quick exclude toggle element:**
```
data-role="quick-exclude"
data-quick-exclude-dimension="<dimension>"
data-quick-exclude-value="<value>"
data-active="true" or data-active="false"
```

Do not vary naming by language or template system. Playwright tests rely on exact
attribute names.

## Failure Modes

| Failure | Consequence |
|---|---|
| Non-zero include count for an excluded value | User sees available rows they cannot actually select |
| Greying the exclude option instead of (or in addition to) the include option | Active filter appears disabled; user loses signal about what is excluded |
| Quick exclude strip state not matching main section state | Two controls show different views of the same filter; user cannot trust either |
| Exclude count computed as 0 instead of rows removed | Exclude options appear meaningless; users cannot judge impact |
| Missing `data-excluded` or `data-active` attributes | Playwright assertions fail; filter state is unverifiable |
| Omitting `data-option-count` on exclude options | Tests cannot verify RULE 2 without parsing visible text |
| Deriving quick excludes dynamically from data | Strip changes unpredictably; breaks predictable Playwright selectors |

## Related Docs

- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/filter-state-and-query-state.md`
- `context/workflows/render-filter-panel-include-exclude-ui.md`
- `examples/canonical-api/fastapi-split-filter-panel-example.py`
