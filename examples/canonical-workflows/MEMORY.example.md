# MEMORY.md

## Current Objective
- Add a `GET /reports/summary` FastAPI endpoint and the matching smoke coverage without changing deployment wiring.

## Current Context
- Active stack: `python-fastapi-uv-ruff-orjson-polars`
- Active archetype: `backend-api-service`
- Active manifest: `backend-api-fastapi-polars`
- Validation target: route smoke plus minimal report-shape verification

## Active Working Set
- `app/api/reports.py`
- `app/services/report_runs.py`
- `tests/smoke/test_health.py`
- `tests/integration/test_report_runs.py`

## Files Already Inspected
- `app/main.py`
- `app/api/reports.py`
- `app/services/report_runs.py`
- `tests/smoke/test_health.py`
- `context/workflows/add-api-endpoint.md`
- `examples/canonical-api/fastapi-endpoint-example.py`

## Important Findings
- The repo already mounts reporting routes through `app/main.py`; no new router registration is needed.
- `report_runs.py` already returns the fields needed for the summary response shape.
- Existing smoke coverage only checks `/health`; route smoke still needs to be added.

## Decisions Already Made
- Keep the new endpoint in `app/api/reports.py`.
  Reason: the existing reporting router already owns adjacent endpoints.
- Add one smoke assertion for the new route before widening integration coverage.
  Reason: this task changes a user-visible happy path but not a new storage boundary.

## Explicitly Not Doing
- Not changing deployment files, Dokku config, or Compose settings.
- Not widening this pass into pagination or filtering behavior.
- Not renaming the existing reporting service surface.

## Blockers Or Risks
- Response model still needs to be aligned with the exact keys returned by `report_runs.py`.
- Smoke test was not updated yet, so the current pause point is not validation-safe.

## Next Steps
- Finalize the response model in `app/api/reports.py`.
- Add route smoke coverage in `tests/smoke/test_health.py` or split out a route-focused smoke file if the current file becomes noisy.
- Run the relevant smoke and integration tests.

## Stop Condition
- Stop again after the endpoint and smoke coverage both pass or after the first failing validation provides a concrete next boundary.

## Last Updated
- 2026-03-12 15:45 local time - code shape chosen, validation still pending
