# Add Source Backoff And Retry

## Purpose

Introduce explicit per-source retry, backoff, and degradation behavior.

## When To Use It

- a source is flaky, rate-limited, or intermittently unavailable
- a new adapter is being promoted from prototype to operational use

## Inputs

- retryable failure classes
- max attempts and cooldown windows
- source-specific rate limits

## Sequence

1. classify failure modes: auth, rate limit, transient upstream, parse, and persistence
2. assign retry policy only to transient classes
3. add exponential backoff with jitter and a ceiling
4. persist source health and cooldown state outside process memory when needed
5. emit operator-visible metrics or logs for retry count, cooldown, and terminal failure
6. test one `429` or timeout path and one non-retryable error path

## Outputs

- explicit retry matrix
- bounded backoff policy
- observable degraded-source behavior

## Related Doctrine

- `context/doctrine/sync-safety-rate-limits.md`

## Common Pitfalls

- retrying parse errors caused by broken selectors or schema changes
- sharing one generic backoff policy across very different sources
- omitting jitter and creating thundering-herd retries

## Stop Conditions

- retry policy still depends on ad hoc exception matching in multiple files
- the repo cannot show which sources are cooling down
- terminal failures are indistinguishable from transient ones
