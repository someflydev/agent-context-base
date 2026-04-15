# Plotly Figure Builder Design

## When To Use This Skill
When adding or refactoring any Plotly chart endpoint.

## The Three-Layer Model

Layer 1 — Aggregation
Input: raw/stored data + filter/query state.
Output: structured aggregate data (series by date, counts by category, etc.).
No Plotly import. Testable with pure data assertions.

Layer 2 — Figure Builder
Input: aggregate data from Layer 1.
Constructs: Plotly figure — traces, layout, config.
Output: structured object (dict / struct / map). NOT a JSON string.
Testable: assert trace count, axis titles, hover templates, label sets.

Layer 3 — Route Handler
Calls Layer 1, then Layer 2.
Serializes the figure to JSON.
Returns the HTTP response.
Contains NO aggregation or figure-construction logic.

## Mandatory Figure Fields
Every figure builder MUST set:
- title (or a paired subtitle with key context)
- xaxis.title (where applicable)
- yaxis.title (where applicable)
- hovertemplate for every trace (never leave as default)
- name for every trace (used as legend labels)
- a metadata dict or annotation: total count, filters applied, date range

## Testing a Figure Builder
A builder is testable if it accepts plain data structures (no DB connections, no HTTP requests). Three minimum test cases:
1. Valid aggregate data: assert trace count and axis title text
2. Empty aggregate data: assert graceful empty-state figure (not a crash)
3. Single-item data: assert valid output shape

## Language-Specific Notes

Python:
- use `plotly.graph_objects.Figure` for builders needing full layout control
- return `figure.to_dict()` from builders; call `figure.to_json()` in the handler
- aggregate in a `services/` module; build figures in a `charts/` or `figures/` module

Go:
- define `PlotlyTrace`, `PlotlyLayout`, `PlotlyFigure` as explicit typed structs
- use `encoding/json` for serialization; no external Plotly Go library needed
- aggregate in an `analytics/` package; build in a `charts/` package

Rust:
- use the `plotly` crate's typed builders (`Plot`, `Scatter`, `Bar`, etc.)
- `serde_json::to_string()` in the handler; return `Plot` from the builder
- aggregate in a `domain::analytics` module; build in a `charts` module

Elixir:
- figure builders return plain Elixir maps (no struct needed)
- `Jason.encode!()` in the controller; figure builder fn lives in a `Charts` module
- aggregate in an `Analytics` context; build in a `Charts` module

## Common Mistakes
- putting aggregation SQL/logic inside the figure builder
- putting figure construction inside the HTTP handler
- returning a JSON string from the builder (breaks testability)
- using `plotly.express` in a builder where full layout control is needed
- leaving hovertemplate unset (defaults are often misleading)
- not testing the empty-data case (graceful empty state is required)