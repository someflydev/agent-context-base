# Cross-Stack Parity Matrix

Status legend: [ ] not started · [~] partial · [x] complete

## Chart Family Parity

| Chart Family          | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| Time Series           | [x]    | [x]| [x]  | [ ]    |
| Category Comparison   | [x]    | [x]| [x]  | [ ]    |
| Distribution          | [x]    | [x]| [x]  | [ ]    |
| Heatmap               | [x]    | [x]| [x]  | [ ]    |
| Funnel                | [x]    | [x]| [x]  | [ ]    |
| Incident Distribution | [x]    | [x]| [x]  | [ ]    |

## Fragment Endpoint Parity

| Endpoint              | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| /fragments/chart      | [x]    | [x]| [x]  | [ ]    |
| /fragments/summary    | [x]    | [x]| [x]  | [ ]    |
| /fragments/details    | [x]    | [x]| [x]  | [ ]    |

## Filter State Parity

| Filter                | Python | Go | Rust | Elixir |
|-----------------------|--------|----|------|--------|
| date_from / date_to   | [x]    | [x]| [x]  | [ ]    |
| services (multi)      | [x]    | [x]| [x]  | [ ]    |
| severity (multi)      | [x]    | [x]| [x]  | [ ]    |
| environment (multi)   | [x]    | [x]| [x]  | [ ]    |

## Verification Parity

| Verification Item         | Python | Go | Rust | Elixir |
|---------------------------|--------|----|------|--------|
| Smoke test: all routes    | [x]    | [x]| [x]  | [ ]    |
| Figure builder unit tests | [x]    | [x]| [x]  | [ ]    |
| Aggregation unit tests    | [x]    | [x]| [x]  | [ ]    |
| Filter-to-chart alignment | [x]    | [x]| [x]  | [ ]    |
| Empty state handling      | [x]    | [x]| [x]  | [ ]    |
| Fixture determinism test  | [x]    | [x]| [x]  | [ ]    |

Update this matrix as each implementation prompt completes.
