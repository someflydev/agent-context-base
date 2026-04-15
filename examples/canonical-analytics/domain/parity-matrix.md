# Cross-Stack Parity Matrix

Status legend: [ ] not started · [~] partial · [x] complete

## Chart Family Parity

| Chart Family          | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| Time Series           | [x]    | [ ]| [ ]  | [ ]    |
| Category Comparison   | [x]    | [ ]| [ ]  | [ ]    |
| Distribution          | [x]    | [ ]| [ ]  | [ ]    |
| Heatmap               | [x]    | [ ]| [ ]  | [ ]    |
| Funnel                | [x]    | [ ]| [ ]  | [ ]    |
| Incident Distribution | [x]    | [ ]| [ ]  | [ ]    |

## Fragment Endpoint Parity

| Endpoint              | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| /fragments/chart      | [x]    | [ ]| [ ]  | [ ]    |
| /fragments/summary    | [x]    | [ ]| [ ]  | [ ]    |
| /fragments/details    | [x]    | [ ]| [ ]  | [ ]    |

## Filter State Parity

| Filter                | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| date_from / date_to   | [x]    | [ ]| [ ]  | [ ]    |
| services (multi)      | [x]    | [ ]| [ ]  | [ ]    |
| severity (multi)      | [x]    | [ ]| [ ]  | [ ]    |
| environment (multi)   | [x]    | [ ]| [ ]  | [ ]    |

## Verification Parity

| Verification Item         | Python | Go | Rust | Elixir |
|---------------------------|--------|----|------|--------|
| Smoke test: all routes    | [x]    | [ ]| [ ]  | [ ]    |
| Figure builder unit tests | [x]    | [ ]| [ ]  | [ ]    |
| Aggregation unit tests    | [x]    | [ ]| [ ]  | [ ]    |
| Filter-to-chart alignment | [x]    | [ ]| [ ]  | [ ]    |
| Empty state handling      | [x]    | [ ]| [ ]  | [ ]    |
| Fixture determinism test  | [x]    | [ ]| [ ]  | [ ]    |

Update this matrix as each implementation prompt completes.
