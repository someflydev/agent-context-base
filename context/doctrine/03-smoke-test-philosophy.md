# Smoke Test Philosophy

Purpose: define fast operational verification.

Rules:

- Smoke tests verify the most important working path quickly.
- They should be easy to run locally and in CI.
- Prefer a small number of trustworthy smokes over many shallow scripts.
- When infra is required, smoke against the isolated test stack.

Prevents:

- slow and noisy smoke suites
- accidental reliance on dev-like data
