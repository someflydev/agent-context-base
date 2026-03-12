# Local RAG Metadata Shape Example

Keep metadata small, stable, and directly useful for answer citation.

Suggested per-chunk document:

```json
{
  "doc_id": "compose-isolation",
  "path": "context/doctrine/compose-port-and-data-isolation.md",
  "section": "Seed And Reset Boundaries",
  "chunk_index": 3,
  "checksum": "sha256:1fb4...",
  "tags": ["docker", "testing", "isolation"]
}
```

Guidelines:

- keep `path` as the exact repo path
- keep `section` human-readable for citations
- keep `checksum` stable for re-index detection
- avoid storing large opaque blobs in metadata

