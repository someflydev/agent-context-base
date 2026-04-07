# TaskFlow Fixture Corpus

Shared fixture data for all terminal canonical examples.

## Files

- `jobs.json`: 20 job records (5 done, 4 failed, 3 running, 8 pending or long-done)
- `events.json`: 30 event records (representative state transitions)
- `config.json`: sample tool configuration

## Schema

Job fields: `id`, `name`, `status`, `started_at`, `duration_s`, `tags`, `output_lines`

Event fields: `event_id`, `job_id`, `event_type`, `timestamp`, `message`

## Usage

Load from the canonical path:

```text
examples/canonical-terminal/fixtures/jobs.json
```

In tests, use the absolute path or a path relative to the example root.
Never hardcode a local filesystem path that won't work after a clone.
