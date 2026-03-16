# Seam: Go + Elixir + Python (Broker + REST)

## Purpose

This example demonstrates both seams in the Go + Elixir + Python trio: Go publishes inference jobs to Elixir via NATS JetStream (async broker seam), and Elixir calls Python for scoring via REST (synchronous seam). The key architectural insight is that Elixir is the coordinator, not a pass-through — it manages the job queue, tracks in-flight inferences, and fans scored results back to NATS for real-time delivery.

This is a **seam-focused example** — it shows only the coordination layer. For a full application scaffold, see `context/archetypes/multi-backend-service.md`.

## Seam Types

**Seam A↔B: Broker (async, decoupled)** — Go publishes `jobs.submitted`; Elixir subscribes.
**Seam B↔C: REST (synchronous)** — Elixir calls Python `POST /score`.

## Why Go Does Not Call Python Directly

Go publishes a job event and its responsibility ends at the NATS boundary. Elixir owns what happens next: it decides which worker process handles the job, manages retries if Python is slow or returns an error, tracks in-flight state per job, and fans the result to downstream consumers (WebSocket clients, Phoenix Channels, other subscribers to `jobs.scored`). If Go called Python directly, all of that coordination would need to live in Go, losing the BEAM's supervisor tree advantage and making each HTTP request block until Python responds.

The async seam means Go can accept thousands of inbound requests without waiting for Python's inference latency. Elixir absorbs that latency inside its own supervision model.

## Event Schemas

### jobs.submitted (Go → Elixir via NATS)

Subject: `jobs.submitted`

```json
{
  "payload_version": 1,
  "correlation_id": "req-abc-001",
  "published_at": "2026-03-16T10:00:00Z",
  "job_id": "job-xyz-42",
  "features": [1.2, 3.4, 5.6, 7.8]
}
```

### POST /score request (Elixir → Python)

```json
{
  "job_id": "job-xyz-42",
  "features": [1.2, 3.4, 5.6, 7.8]
}
```

### POST /score response (Python → Elixir)

```json
{
  "job_id": "job-xyz-42",
  "score": 0.625,
  "label": "medium_value"
}
```

### jobs.scored (Elixir → NATS, fan-out result)

Subject: `jobs.scored`

```json
{
  "payload_version": 1,
  "correlation_id": "req-abc-001",
  "job_id": "job-xyz-42",
  "score": 0.625,
  "label": "medium_value",
  "scored_at": "2026-03-16T10:00:01Z"
}
```

## How to Run Locally

```bash
cd examples/canonical-multi-backend/trios/go-elixir-python
docker compose up --build
```

Expected sequence:
1. NATS starts and passes its healthcheck.
2. `python-service` starts and passes its healthcheck.
3. `elixir-service` starts after NATS and Python are healthy; subscribes to `jobs.submitted`.
4. `go-service` starts after NATS and Elixir are healthy; ensures the `JOBS` stream; publishes one demo job.
5. Elixir receives the job, calls Python `/score`, logs the result, and publishes to `jobs.scored`.

## What to Observe

- Go log: `published job_id=job-demo-001 to jobs.submitted (seq=1)`
- Elixir log: `received job_id=job-demo-001 from jobs.submitted`
- Elixir log: `scored job_id=job-demo-001 score=0.45 label=low_value`
- Elixir log: `published jobs.scored for job_id=job-demo-001`
- Python log: uvicorn access log `POST /score 200`
- NATS monitoring: `curl http://localhost:8222/jsz` shows stream `JOBS` with at least 1 message
- Health endpoints:
  - `curl http://localhost:8080/healthz` → `{"status":"ok"}` (Go checks NATS)
  - `curl http://localhost:4000/healthz` → `{"status":"ok"}` (Elixir)
  - `curl http://localhost:8002/healthz` → `{"status":"ok"}` (Python)

Trigger an additional job:

```bash
curl -X POST http://localhost:8080/submit-job \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: req-manual-001" \
  -d '{"job_id": "job-manual-001", "features": [8.0, 9.0, 7.5, 8.5]}'
```

Expected response: `{"status":"accepted","job_id":"job-manual-001","seq":2}`

## Verifying Each Seam

**Seam A (Go → Elixir via NATS):** Check that Elixir logs a "received job_id=..." line for every job Go publishes. Check NATS monitoring at `http://localhost:8222/jsz` for message count.

**Seam B (Elixir → Python via REST):** Check that Python's access log shows a `POST /score 200` for each job. Check that Elixir logs "scored job_id=... score=..." after each Python response.

**Full round-trip:** Submit a job via Go's `/submit-job` and watch all three logs activate: Go publishes, Elixir receives and calls Python, Python scores, Elixir publishes the result.

## Dependency Order

Python starts first (no dependencies). NATS starts independently. Elixir waits for both NATS and Python. Go waits for NATS and Elixir (which already implies Python is healthy). This ordering ensures no service sends work before its downstream is ready.

## Related

- `context/doctrine/multi-backend-coordination.md`
- `context/stacks/trio-go-elixir-python.md`
- `context/stacks/duo-go-elixir.md`
- `context/stacks/duo-go-python.md`
- `context/stacks/coordination-seam-patterns.md`
- `context/stacks/go-echo.md`
- `context/stacks/elixir-phoenix.md`
- `context/stacks/python-fastapi-uv-ruff-orjson-polars.md`
- `context/stacks/nats-jetstream.md`
