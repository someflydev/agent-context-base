# Minimal Fixture Datasets

These fixtures stay intentionally small so descendant repos can copy them without inheriting test bloat.

## Included Fixtures

- `minimal-report-runs.json`: tiny tabular seed shape for API and storage tests
- `minimal-document-corpus.jsonl`: tiny document corpus for local RAG or indexing tests

## Rule

Prefer the smallest deterministic fixture that proves a boundary. Add volume only when the behavior genuinely depends on it.
