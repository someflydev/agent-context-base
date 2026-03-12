# Add Local RAG Indexing

Use this workflow when adding local retrieval, chunking, indexing, or question-answer behavior.

## Preconditions

- the corpus source is known
- the vector or search backend is known
- the retrieval contract is simple enough for a first pass

## Sequence

1. define ingestion inputs and retrieval outputs
2. choose one primary indexing path
3. implement deterministic local ingestion for a tiny corpus
4. add smoke coverage for one ingest-plus-query flow
5. add minimal real-infra integration tests for vector or search backend behavior
6. document where embeddings, chunks, and indexes live

## Outputs

- local indexing path
- retrieval path
- smoke and integration coverage

## Related Docs

- `context/archetypes/local-rag-system.md`
- `context/stacks/qdrant.md`
- `examples/canonical-rag/README.md`

## Common Pitfalls

- mixing too many backends in the first pass
- no deterministic tiny corpus for tests
- assuming vector search correctness from unit tests alone

