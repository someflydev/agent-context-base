# Raw Data Retention

Raw retention is the default posture for source-backed systems unless storage, policy, or terms make it impractical.

## Default Rule

- archive raw responses, downloaded files, or scraped documents before parsing when the payload size is reasonable
- keep retention layout deterministic so operators can find a raw capture from a normalized row
- store metadata beside the payload: source, fetched_at, request fingerprint, content type, checksum, and status

## Retention Shape

- partition by source and fetch date or sync run
- keep payload body separate from parse outputs
- prefer append-only storage for raw artifacts
- make raw paths stable enough for re-parse jobs and failure triage

## When To Trim

- legal, licensing, or privacy constraints can override default retention
- oversized binary captures can move to sampled retention if full archival is too costly
- if retention is reduced, document the rule and preserve enough metadata to explain the omission

## Assistant Guardrails

- do not overwrite prior raw captures in place unless the repo already uses a content-addressed archive
- do not treat parsed tables as a substitute for raw retention
- do not mix dev and test raw archives

## Verification Rule

For the first retained source, verify one round trip from raw artifact to parsed record and one operator-friendly lookup path.
