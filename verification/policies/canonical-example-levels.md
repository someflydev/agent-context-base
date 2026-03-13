# Canonical Example Levels

Verification levels describe how much trust a maintainer or assistant should place in a canonical example.

## Levels

- `draft`
  Useful guidance only. Do not prefer it over a verified nearby example.
- `syntax-checked`
  Parses or loads cleanly and passes structural assertions.
- `smoke-verified`
  Runs through a minimal harness or container request path.
- `behavior-verified`
  Proves a core behavior shape such as route output, seed isolation, or CLI output.
- `golden`
  Stable and strongly preferred when a task matches.

## CI Tiers

### Fast checks

Run on every local pass and every CI push:

- `verification/unit/test_repo_integrity.py`
- `verification/unit/test_prompt_rules.py`
- `verification/unit/test_manifests.py`
- `verification/unit/test_alias_catalog.py`
- `verification/scripts/test_repo_scripts.py`
- static data checks

These checks should avoid external runtimes and should finish quickly.

### Medium checks

Run in normal CI when Python is available and Docker is allowed:

- Python example harness tests
- data artifact tests
- Docker builds for the canonical FastAPI, Go Echo, and Rust Axum runtime bundles when `VERIFY_DOCKER=1`

These checks verify that the repository still points to runnable examples without forcing every local machine to install every toolchain.

### Heavy checks

Run in scheduled CI, release checks, or explicit local passes:

- full Go and Rust scenario runs
- future multi-container harnesses
- any heavier stack-specific verification added later

Heavy checks should remain selective by stack so maintainers can expand coverage without turning every local run into a full language-lab build.

## Policy Rules

- New canonical examples should land with at least `syntax-checked`.
- A runtime example should not be marked `smoke-verified` without a harness or Docker check.
- A verified example should name its test file and scenario harness in repo docs.
- If two examples compete for the same task, prefer the one with the higher verification level and higher confidence.
