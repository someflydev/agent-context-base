# Verification Framework

Canonical examples only help if they stay correct. In a repo that teaches assistants how to build real systems, an untested example is worse than no example at all: it looks authoritative, gets copied into generated code, and spreads silent drift into manifests, prompts, helper scripts, and downstream repos.

This verification layer makes example trust explicit. Each canonical example now has:

- a registry entry
- a verification level
- a confidence rating
- one or more concrete verification targets
- a scenario harness when runtime checks exist

That structure improves assistant reliability because selection logic can prefer verified examples over merely present ones.

## Why Verification Matters

- Canonical examples become generation inputs. If they drift, assistants reproduce that drift.
- Untested prompts and manifests create false confidence because the repository still looks coherent on casual inspection.
- Maintenance scripts can silently regress even when prose docs remain accurate.
- Stack expansion becomes risky when there is no repeatable way to prove a new example still parses, boots, or responds.

## Verification Layers

- Repo integrity
  Required directories, manifests, templates, examples, registry entries, and documented references stay aligned.
- Prompt rules
  Prompt-first repositories keep monotonic numbering, suffix discipline, and valid cross-file references.
- Script verification
  Python maintenance helpers still bootstrap repos, preview bundles, initialize memory, and create handoff snapshots.
- Example verification
  Canonical examples parse, import, and execute through lightweight harnesses where feasible.
- Docker verification
  Runtime-heavy API examples build and answer a minimal request without forcing every machine to install every toolchain.
- Data artifact verification
  JSON and YAML examples load, expose required keys, and avoid placeholder drift.

## Example Maturity Ladder

- `draft`
  The example is tracked but only verified for presence and metadata.
- `syntax-checked`
  The example parses or loads successfully and passes structural assertions.
- `smoke-verified`
  The example runs through a minimal harness or container request path and proves its primary surface works.
- `behavior-verified`
  The example proves one real behavior beyond boot, such as route output, deterministic data ordering, or CLI output shape.
- `golden`
  The example is strongly verified, stable, and should be preferred when multiple examples could satisfy the same task.

## Directory Structure

- `verification/README.md`
  Verification philosophy, trust model, and maturity ladder.
- `verification/example_registry.yaml`
  The authoritative list of canonical examples, verification levels, targets, confidence, Docker posture, and scenario harnesses.
- `verification/stack_support_matrix.yaml`
  Per-stack maturity view used to track verified coverage and known gaps.
- `verification/policies/`
  CI and policy documents describing fast, medium, and heavy verification tiers.
- `verification/unit/`
  Fast structural tests for repo integrity, manifests, prompts, and alias metadata.
- `verification/scripts/`
  Tests for Python maintenance scripts and helper CLIs.
- `verification/examples/`
  Stack-specific verification suites for Python, Nim, Go, Rust, Elixir, and static data examples.
- `verification/scenarios/`
  Minimal harness helpers that mount, run, or probe canonical examples.
- `verification/fixtures/`
  Tiny valid and broken repo shapes used to exercise script and policy behavior.

## Execution Model

- Local
  `scripts/run_verification.py --tier fast` gives a no-runtime baseline.
- Selective
  `scripts/verify_examples.py --stack python-fastapi-uv-ruff-orjson-polars` narrows to one stack.
- Incremental
  `scripts/verify_examples.py --example fastapi-endpoint-example` targets one example or bundle.
- CI
  Fast checks run by default, medium checks enable harnesses and Docker, heavy checks handle Go and Rust builds.

## Design Constraints

- Local runs should not require every language toolchain.
- Docker-backed examples should use small official base images and minimal dependencies.
- Adding a new stack should mainly require a registry entry, a harness or parser test, a support-matrix update, and optional Docker metadata.
- Assistant-facing ranking should prefer higher verification levels and higher confidence when task relevance is otherwise similar.
