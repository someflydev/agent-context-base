# Render Filter Panel Include/Exclude UI

## Purpose

Render a correct filter panel with split include/exclude options per dimension,
proper visual states for excluded values, exclude impact counts, and an optional
quick-excludes strip. Applies to any stack (Python/FastAPI, Elixir/Phoenix, etc.).

## When To Use It

- Building any HTMX-served filter panel with include/exclude semantics
- Adding quick excludes to an existing filter panel
- Verifying that a filter panel's visual state matches backend query state

## Sequence

### Step 1 — Render the quick-excludes strip (if configured)

Declare quick excludes as a backend constant:
```python
QUICK_EXCLUDES = [("status", "archived"), ("status", "paused")]
```

For each configured `(dimension, value)` pair:

- Compute `exclude_impact_counts(state, dimension)[value]` as the preview badge count.
- Render a toggle (checkbox or button) with:
  - `data-role="quick-exclude"`
  - `data-quick-exclude-dimension="<dimension>"`
  - `data-quick-exclude-value="<value>"`
  - `data-active="true"` if value is in D_out, `"false"` otherwise
  - A visible badge showing the impact count
  - Highlighted/checked visual state when active

Place the strip at the top of the filter panel, above the dimension groups.

### Step 2 — Render per-dimension groups

For each facet dimension, render a section with a heading and two sub-sections:

**Include sub-section** (one labeled checkbox per option):

- Compute include counts using the normal `facet_counts(state, dimension)` path.
- For each option:
  - If the option is in D_out (RULE 1):
    - Force count to 0; do not use the `facet_counts` result.
    - Add `data-excluded="true"` to the option element.
    - Add `disabled` to the checkbox input.
    - Apply `opacity-50 cursor-not-allowed` to the label.
  - Otherwise: use the normal include count, no greying.

**Exclude sub-section** (one labeled checkbox per option):

- Compute exclude impact counts using `exclude_impact_counts(state, dimension)`.
- For each option:
  - If the option is in D_out (RULE 2 + RULE 3b):
    - Mark the checkbox as checked.
    - Add `data-active="true"` to the option element.
    - Apply an active highlight style (e.g., `border-red-200 bg-red-50`).
  - Show the impact count badge regardless of active state.
  - If this option is also a configured quick exclude, the same `data-active` value
    must be consistent with the quick exclude toggle in the strip.

### Step 3 — Carry all required data-* attributes

Every option element (label) must have:

Include option:
```
data-filter-dimension="<dimension>"
data-filter-option="<value>"
data-filter-mode="include"
data-option-count="<N>"       -- 0 when value is in D_out
data-excluded="true"          -- only when value is in D_out
```

Exclude option:
```
data-filter-dimension="<dimension>"
data-filter-option="<value>"
data-filter-mode="exclude"
data-option-count="<N>"       -- exclude impact count
data-active="true"            -- only when value is in D_out
```

### Step 4 — Include the filter panel in the HTMX form

Include the filter panel in the same `<form>` as the result list, or use
`hx-swap-oob` if the panel updates independently. The HTMX trigger should be
`change` or `submit` so filter state propagates on every checkbox change.

Quick exclude toggles and main-section exclude checkboxes should share the same
`name` and `value` attributes (`name="<dim>_out"`, `value="<val>"`). The backend
normalizes duplicates. Both are `checked` when the value is in D_out.

### Step 5 — Write Playwright assertions

Verify at minimum:

```ts
// RULE 1: excluded value's include option has count 0 and is disabled
const includeOpt = page.locator('[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="include"]');
await expect(includeOpt).toHaveAttribute("data-option-count", "0");
await expect(includeOpt).toHaveAttribute("data-excluded", "true");
await expect(includeOpt.locator("input[type=checkbox]")).toBeDisabled();

// RULE 2: excluded value's exclude option has non-zero count and is checked
const excludeOpt = page.locator('[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="exclude"]');
await expect(excludeOpt).toHaveAttribute("data-active", "true");
await expect(excludeOpt.locator("input[type=checkbox]")).toBeChecked();

// RULE 3: quick exclude toggle matches main section state
const qe = page.locator('[data-role="quick-exclude"][data-quick-exclude-value="archived"]');
await expect(qe).toHaveAttribute("data-active", "true");
```

## Outputs

- A backend function rendering a complete include/exclude filter panel fragment
- A `QUICK_EXCLUDES` config constant if quick excludes are used
- An `exclude_impact_counts(state, dimension)` function (separate from `facet_counts`)
- Playwright tests covering RULE 1, RULE 2, and RULE 3 assertions

## Related Doctrine

- `context/doctrine/filter-panel-rendering-rules.md`
- `context/doctrine/faceted-query-count-discipline.md`
- `context/doctrine/filter-state-and-query-state.md`

## Common Pitfalls

- Computing include counts for excluded values using the normal `facet_counts` path,
  which returns non-zero. Must short-circuit to 0 when the value is in D_out.
- Greying the exclude option in addition to or instead of the include option.
- Quick exclude toggles using separate hidden inputs that can desync from main
  section checkboxes. Prefer shared `name`/`value` inputs or OOB sync.
- Rendering the quick excludes strip without corresponding entries in the main
  exclude section.
- Omitting `data-excluded` or `data-active` attributes that break Playwright assertions.
- Naming the impact-count function `facet_counts` or confusing it with the include
  count function — keep them clearly separate with distinct names.

## Stop Conditions

- A Playwright test confirms RULE 1 for at least one excluded value (count=0, disabled, data-excluded).
- A Playwright test confirms RULE 2 for at least one excluded value (non-zero count, data-active).
- A Playwright test confirms RULE 3: quick exclude toggle and main section exclude
  option both reflect the same active state.
