# Tailwind Utility-First Styling

## Purpose
Tailwind is the canonical styling layer for server-rendered analytics UIs in this repository. It pairs exceptionally well with HTMX and Plotly by allowing developers to style fragments and components without leaving the template file. Avoiding ad hoc inline styles or secondary CSS methodologies ensures a consistent, maintainable, and predictable design system.

## Assumptions
- Tailwind is loaded via CDN script or bundled via postcss/tailwindcss CLI.
- The full class list is available (no arbitrary purge rules breaking development).
- Dark mode is opt-in and toggled via a class or data attribute, not system pref.

## Rules

Rule 1 — Use Tailwind utilities for all interactive state expression.
Active, disabled, selected, loading, and error states must be expressed via Tailwind utility classes, not inline styles or bespoke CSS class names.

Rule 2 — Follow filter-panel-rendering-rules.md for the filter UI class contract.
The include/exclude panel class contract (`opacity-50 cursor-not-allowed`, `data-excluded`, etc.) is defined there. Tailwind classes in filter panels are not arbitrary — they are part of the backend-to-frontend contract.

Rule 3 — Keep layout logic in templates, not in Python/Go/Rust/Elixir code.
Do not generate Tailwind class strings in backend code. Template files own layout decisions. Backend code may conditionally pass a flag or enum, but the class-string resolution belongs in the template.

Rule 4 — Use semantic naming for repeated component patterns.
When a set of utilities is repeated across templates (e.g., a count badge, a filter pill, a chart card border), extract it to a named template component or partial. Do not scatter identical utility strings across 20 templates.

Rule 5 — Prefer prose- and screen-reader-friendly label patterns.
Every interactive control needs a visible or sr-only label. Do not rely on placeholder text or icon-only affordances for filter controls.

Rule 6 — Tailwind is the only CSS methodology in this stack.
Do not mix Tailwind with Bootstrap, Bulma, or bespoke CSS frameworks. Scoped component CSS is acceptable only where Tailwind genuinely cannot express the layout (rare). Document the exception in a comment.

## Existing Usage in This Repo
- `context/doctrine/filter-panel-rendering-rules.md` — defines the include/exclude class contract.
- `context/doctrine/backend-driven-ui-correctness.md` — states that Tailwind classes should improve readability, not hide missing state markers.
- `context/stacks/backend-driven-ui-htmx-tailwind-plotly.md` — the multi-stack support surface for HTMX + Tailwind + Plotly.

## What This Doctrine Does NOT Cover
- CSS-in-JS, styled-components, or frontend build toolchains beyond Tailwind CLI.
- Plotly chart styling (controlled via Plotly layout templates, not Tailwind).
- Non-analytics repo types (Tailwind may or may not be appropriate).