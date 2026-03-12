# Elasticsearch

Use this pack when the repo needs richer search, indexing pipelines, or aggregation behavior than Meilisearch is meant to cover.

## Typical Repo Surface

- index mappings
- client bootstrap
- indexing services
- query adapters
- operational reset or reindex tooling

## Change Surfaces To Watch

- index names and aliases
- mappings and analyzers
- bulk indexing behavior
- query DSL assumptions

## Testing Expectations

- use real isolated Elasticsearch for integration tests
- prove index creation or mapping application if the feature depends on it
- verify one representative query and one indexing path

## Common Assistant Mistakes

- treating mappings as incidental config
- testing against mocks only
- ignoring version-sensitive behavior in queries or analyzers

