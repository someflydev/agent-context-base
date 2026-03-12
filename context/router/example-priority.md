# Example Priority

Canonical examples are loaded after doctrine and workflows, not before.

Priority rules:

1. prefer the example marked preferred for the pattern family
2. use a secondary example only if the preferred one is incompatible with the active stack
3. ignore retired examples unless no active example exists and the gap must be explained

Pattern families should have one preferred example each for:

- prompt sequence layout
- API endpoint shape
- HTMX fragment flow
- smoke test structure
- Docker Compose dev/test isolation
