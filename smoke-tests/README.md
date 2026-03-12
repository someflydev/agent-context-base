# Smoke Tests

This folder is reserved for fast operational verification.

Guidelines:

- one scenario should prove the primary happy path works
- Docker-backed smoke tests should target the isolated test stack
- do not let smoke scripts mutate dev-like data
