# Cross-Stack Parity Matrix

Status legend: [ ] not started · [~] partial · [x] complete

## Chart Family Parity

| Chart Family          | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| Time Series           | [x]    | [x]| [ ]  | [ ]    |
| Category Comparison   | [x]    | [x]| [ ]  | [ ]    |
| Distribution          | [x]    | [x]| [ ]  | [ ]    |
| Heatmap               | [x]    | [x]| [ ]  | [ ]    |
| Funnel                | [x]    | [x]| [ ]  | [ ]    |
| Incident Distribution | [x]    | [x]| [ ]  | [ ]    |

## Fragment Endpoint Parity

| Endpoint              | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| /fragments/chart      | [x]    | [x]| [ ]  | [ ]    |
| /fragments/summary    | [x]    | [x]| [ ]  | [ ]    |
| /fragments/details    | [x]    | [x]| [ ]  | [ ]    |

## Filter State Parity

| Filter                | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| date_from / date_to   | [x]    | [x]| [ ]  | [ ]    |
| services (multi)      | [x]    | [x]| [ ]  | [ ]    |
| severity (multi)      | [x]    | [x]| [ ]  | [ ]    |
| environment (multi)   | [x]    | [x]| [ ]  | [ ]    |

## Verification Parity

| Verification Item         | Python | Go | Rust | Elixir |
|---------------------------|--------|----|------|--------|
| Smoke test: all routes    | [x]    | [x]| [ ]  | [ ]    |
| Figure builder unit tests | [x]    | [x]| [ ]  | [ ]    |
| Aggregation unit tests    | [x]    | [x]| [ ]  | [ ]    |
| Filter-to-chart alignment | [x]    | [x]| [ ]  | [ ]    |
| Empty state handling      | [x]    | [x]| [ ]  | [ ]    |
| Fixture determinism test  | [x]    | [x]| [ ]  | [ ]    |

Update this matrix as each implementation prompt completes.
