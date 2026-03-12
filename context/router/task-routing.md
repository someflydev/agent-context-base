# Task Routing

Infer task type from plain English first. The operator should not need to memorize internal names.

Routing rules:

- feature addition -> `context/workflows/add-feature.md`
- API route or handler change -> `context/workflows/add-api-endpoint.md`
- CLI change -> `context/workflows/extend-cli.md`
- storage/search/queue addition -> `context/workflows/add-storage-integration.md`
- prompt-sequence work -> `context/workflows/generate-prompt-sequence.md`
- post-run refinement -> `context/workflows/post-flight-refinement.md`
- smoke verification -> `context/workflows/add-smoke-tests.md`

Stack inference sources:

1. repo profile manifest
2. lockfiles and tool files
3. dominant source tree
4. canonical examples already present

If stack inference conflicts across these sources, stop and surface the mismatch.
