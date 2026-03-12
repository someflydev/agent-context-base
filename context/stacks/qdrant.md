# Qdrant

Use this pack when the repo needs local vector storage and retrieval for RAG or semantic search features.

## Typical Repo Surface

- embedding pipeline
- chunking rules
- collection setup
- query adapters
- tiny local corpus fixtures

## Change Surfaces To Watch

- collection names
- vector dimensions
- payload shape
- filter behavior

## Testing Expectations

- smoke test one ingest-plus-query path only if it is a main user path
- integration test real collection creation, insertion, and retrieval against isolated test Qdrant
- keep the corpus tiny and deterministic

## Common Assistant Mistakes

- no fixed tiny corpus for verification
- assuming embedding and retrieval correctness from unit tests alone
- mixing experimental retrieval strategies into the first canonical path

