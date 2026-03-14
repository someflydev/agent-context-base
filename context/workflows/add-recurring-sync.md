# Add Recurring Sync

## Purpose

Schedule repeatable source syncs such as twice-daily pulls without coupling schedule logic to fetch internals.

## When To Use It

- the repo needs periodic acquisition
- operators need stable recurring windows instead of manual sync triggers

## Inputs

- source names
- target cadence
- timeout and concurrency limits

## Sequence

1. define cadence, timezone, and overlap policy explicitly
2. schedule lightweight sync requests that reference source and window only
3. ensure a duplicate scheduled run is safe through idempotency or locking
4. store last-success and last-failure state per source
5. add operator-facing status for next run, last run, and degraded sources

## Outputs

- recurring sync config
- per-source schedule metadata
- observable sync status

## Related Doctrine

- `context/doctrine/sync-safety-rate-limits.md`
- `context/doctrine/data-acquisition-philosophy.md`

## Common Pitfalls

- doing the full sync inline inside the scheduler
- ambiguous timezone handling
- allowing overlapping runs for the same source without an explicit policy

## Stop Conditions

- the cadence cannot be explained in one sentence with absolute timing
- duplicate scheduled runs produce non-idempotent writes
- operators cannot see last success or failure per source
