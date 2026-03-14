# Add API Ingestion Source

## Purpose

Add a new API-backed source adapter with raw archival and bounded sync behavior.

## When To Use It

- the upstream offers an API, feed, or export endpoint
- the repo needs structured acquisition with repeatable pulls

## Inputs

- source contract and auth method
- pagination or cursor model
- retention location for raw payloads
- normalized target shape

## Sequence

1. document endpoint, auth, pagination, and rate-limit rules
2. implement a narrow adapter that only fetches and returns raw payload units
3. write raw payloads to the archive before parsing when practical
4. add checkpointing for cursor or window progress
5. parse raw artifacts into normalized records in a separate stage
6. add one smoke path and one real boundary test for sync behavior or persistence

## Outputs

- source adapter
- raw archive writes
- parser handoff contract

## Related Doctrine

- `context/doctrine/data-acquisition-philosophy.md`
- `context/doctrine/raw-data-retention.md`
- `context/doctrine/sync-safety-rate-limits.md`

## Common Pitfalls

- mixing fetch and parse logic in the same function
- discarding headers or cursor metadata needed for replay
- checkpointing before the raw payload is durably written

## Stop Conditions

- the adapter cannot replay a single page or window safely
- rate-limit handling is still implicit or missing
- normalized rows cannot be traced back to source payloads
