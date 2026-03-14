# Canonical Example Levels

Verification levels describe how much trust maintainers and assistants should place in a canonical example.

## Levels

- `draft`
  Tracked and documented, but not yet structurally validated.
- `syntax-checked`
  Parses or loads cleanly and passes static assertions.
- `smoke-verified`
  Boots in a minimal harness or container and proves the main entrypoint works.
- `behavior-verified`
  Proves at least one meaningful behavior such as response shape, deterministic ordering, or CLI output mode.
- `golden`
  Stable, behavior-rich, and the preferred example for generation when it matches the task.

## CI Tiers

### Fast checks

Run on every local pass and every CI push:

- `verification/unit/test_repo_integrity.py`
- `verification/unit/test_prompt_rules.py`
- `verification/unit/test_manifests.py`
- `verification/unit/test_alias_catalog.py`
- `verification/scripts/test_repo_scripts.py`
- `verification/examples/data/test_yaml_json_examples.py`
- Python syntax-oriented example checks that do not require Docker

These checks avoid external runtimes and should stay cheap enough for normal local use.

### Medium checks

Run in standard CI when Python is available and Docker is permitted:

- Python scenario harness tests
- data artifact tests
- Docker builds and HTTP probes for the canonical FastAPI, Go Echo, and Rust Axum runtime bundles when `VERIFY_DOCKER=1`

These checks prove that runtime examples remain buildable without forcing every contributor to install every language toolchain.

### Heavy checks

Run on scheduled CI, release gates, or explicit local passes:

- native Go scenario runs when `go` is available
- native Rust scenario runs when `cargo` is available
- future multi-container or cross-service scenario harnesses

Heavy checks should remain selectable by stack so expanding coverage does not make every local pass expensive.

## Policy Rules

- New canonical examples should land with at least `syntax-checked`.
- Shared invariant or index files may be `syntax-checked`, but that does not justify claiming a stack-specific implementation exists.
- Runtime examples should not be marked `smoke-verified` without a harness or Docker probe.
- `behavior-verified` examples should assert one outcome, not only boot.
- Registry metadata, README metadata, and test coverage should agree on verification level and harness name.
- Capability README matrices, registry metadata, and stack support posture should agree on whether a stack has a real example or only the invariant layer.
- When assistants choose between multiple relevant examples, they should prefer the higher verification level and higher confidence entry.
