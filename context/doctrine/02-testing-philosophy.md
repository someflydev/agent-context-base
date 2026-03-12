# Testing Philosophy

Purpose: define the minimum quality bar across repo types.

Rules:

- Unit tests are not enough for significant persistence, queue, search, or cross-service changes.
- Add minimal mostly happy-path real-infra integration tests with a few edge cases.
- Keep tests targeted and explicit about the boundary being exercised.
- Prefer real containers over mocks when infrastructure behavior matters.

Prevents:

- false confidence from mock-only coverage
- untested storage integration
- regressions at service boundaries
