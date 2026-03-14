# Sync Safety And Rate Limits

Acquisition speed is secondary to source safety and repeatable sync behavior.

## Respect The Source

- follow published rate limits, robots directives, and terms where relevant
- identify the client clearly when the source expects it
- prefer bounded concurrency per source instead of one global worker pool

## Backoff Discipline

- retry only for transient failures
- use exponential backoff with jitter
- cap total attempts and emit state for operator review when a source stays degraded
- treat `429`, `503`, connection resets, and timeouts differently from hard auth or schema failures

## Idempotent Sync Behavior

- each sync unit should be safe to re-run after a crash or duplicate event
- checkpoint only after the durable stage that justifies progress movement
- schedule lightweight sync requests; do not bury long-running fetches inside the scheduler itself

## Partial Failure Rule

- one failing source must not stall all unrelated sources
- retain failure metadata and last-success state per source
- replay from the smallest failed unit: page, cursor, file, or run window

## Anti-Patterns

- aggressive retry loops without jitter
- scraping at API-like concurrency against fragile HTML pages
- mutating frontend-visible state before the source write path is durable

## Stop Rule

If the implementation cannot explain how `429`, duplicate delivery, crash-after-fetch, and partial window failure behave, the sync design is incomplete.
