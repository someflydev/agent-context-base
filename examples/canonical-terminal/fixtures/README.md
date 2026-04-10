# TaskFlow Fixture Corpus

Shared fixture data for all terminal canonical examples.

## Files

- `jobs.json`: 20 job records (5 done, 4 failed, 3 running, 8 pending or long-done)
- `events.json`: 30 event records (representative state transitions)
- `config.json`: sample tool configuration

## Extended Fixtures

- `jobs-large.json`: 100 job records with varied statuses, long names, empty
  outputs, Unicode tags, and scroll-heavy logs
- `events-large.json`: 300 event records for the large corpus with
  chronologically consistent replay data
- `fixtures-edge-cases.json`: 10 explicit edge-case records for targeted
  robustness tests
- `replay/`: fixture-backed replay helpers for Python and Go

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

## Usage: Large Corpus

Set `TASKFLOW_FIXTURES_PATH=examples/canonical-terminal/fixtures/` and pass
`--fixtures-file jobs-large.json` to use the large corpus.

Examples that accept a direct fixtures path can continue using the directory
and specific file directly.

```text
TASKFLOW_FIXTURES_PATH=examples/canonical-terminal/fixtures/
--fixtures-file jobs-large.json
```

The shared harness also supports `--large-corpus` as a convenience mode; it
rewrites the corpus to `jobs-large.json` and `events-large.json` for runners
that still expect the default fixture filenames.
