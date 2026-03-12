# Local RAG System

Use this archetype for repos centered on local ingestion, indexing, retrieval, and answer generation over a bounded corpus.

## Common Goals

- deterministic tiny corpus
- explicit chunking and indexing behavior
- reliable local retrieval
- clear storage and embedding boundaries

## Required Context

- `context/workflows/add-local-rag-indexing.md`
- `context/stacks/qdrant.md`
- any supporting search or storage stack docs

## Common Workflows

- `context/workflows/add-local-rag-indexing.md`
- `context/workflows/add-storage-integration.md`
- `context/workflows/add-smoke-tests.md`

## Likely Examples

- `examples/canonical-rag/README.md`
- `examples/canonical-storage/README.md`

## Typical Anti-Patterns

- no tiny reproducible corpus
- many retrieval strategies in the first pass
- no real vector-store verification

