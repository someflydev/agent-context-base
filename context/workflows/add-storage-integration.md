# Add Storage Integration

Purpose: add persistence, queue, or search infrastructure safely.

Sequence:

1. load the storage stack pack and compose doctrine
2. define config surface and data path isolation
3. add connection logic in one clear layer
4. add seed/reset behavior with separate test paths
5. add minimal real-infra integration tests

Pitfalls:

- ad hoc ports
- shared dev/test volumes
- mock-only verification
