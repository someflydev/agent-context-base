# Verification Contract

Each implementation must pass all items in this contract before it is marked
[x] in the parity matrix and CATALOG.md.

## Smoke Tests (required; run against live server)

Every route listed in spec.md must return HTTP 200 with no server error.

Minimum routes to smoke-test:
  GET /                      → 200, HTML response
  GET /trends                → 200, HTML response
  GET /services              → 200, HTML response
  GET /distributions         → 200, HTML response
  GET /heatmap               → 200, HTML response
  GET /funnel                → 200, HTML response
  GET /incidents             → 200, HTML response
  GET /health                → 200, {"status": "ok"} JSON
  GET /fragments/chart?view=trends → 200, HTML fragment containing plotly JSON
  GET /fragments/summary?view=trends → 200, HTML fragment with text content

## Figure Builder Unit Tests (required; no server needed)

For each of the six chart families, there must be a unit test covering:
  1. valid aggregate input → assert trace count ≥ 1 and axis titles non-empty
  2. empty aggregate input → assert a valid figure is returned (not an error)
  3. single-item aggregate input → assert valid output shape

## Aggregation Unit Tests (required; no server or DB needed)

For each chart family's aggregation function:
  1. smoke fixture input → assert output matches expected shape and row count
  2. filtered input (e.g., one service, one environment) → assert filtered output

## Filter State Alignment Tests (required)

For each chart family:
  - Apply a filter (e.g., services=["service-A"]) and assert that both the
    visible results and the chart data reflect the same filtered set.
  - Assert: chart trace labels or x-axis values do not include filtered-out values.

## Fixture Determinism Test (required)

Run generate_fixtures.py twice. Assert the output files are byte-identical.

## Empty State Test (required)

Pass an empty or zero-result filter state to each chart endpoint.
Assert the response is HTTP 200 and the figure contains an appropriate empty-state
trace or annotation (not a 500 error).

## Parity Alignment Check (required before marking complete)

Run the arc's parity check runner (PROMPT_133 will create it):
  python3 verification/analytics/run_parity_check.py --stack <python|go|rust|elixir>
