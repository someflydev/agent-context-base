# Meilisearch

Use this pack when the repo adds straightforward full-text search with fast local setup.

## Typical Repo Surface

- search client setup
- indexing jobs or hooks
- search query adapters
- seed or fixture indexing helpers

## Change Surfaces To Watch

- index names
- document shape
- ranking or filter settings
- reindex triggers

## Testing Expectations

- smoke test only the top-level app flow if search powers a primary path
- integration test real indexing plus one real query against isolated test infrastructure
- use tiny deterministic documents

## Common Assistant Mistakes

- treating search as pure application logic
- forgetting to test reindex timing or explicit index creation
- mixing dev and test indexes in one local instance without isolation

