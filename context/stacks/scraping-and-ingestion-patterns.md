# Scraping And Ingestion Patterns

Use this pack when the repo adds API clients, scrape adapters, raw capture, and parser boundaries for external sources.

## Typical Repo Surface

- source adapter modules
- shared HTTP client and pacing helpers
- raw archive root
- parser or selector modules
- sync status and retry configuration

## Change Surfaces To Watch

- auth headers and user-agent posture
- pagination and cursor semantics
- robots or terms constraints
- selector brittleness and document layout assumptions
- content-addressing or checksum logic in raw retention

## Testing Expectations

- verify one source path from fetch to raw archive
- parse from archived payloads, not only from live responses
- keep dev and test archives isolated

## Common Assistant Mistakes

- skipping raw archival because the payload already looks structured
- coupling CSS selectors to orchestration code
- assuming scraping and API sources can share the same retry policy unchanged
