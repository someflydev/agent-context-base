# Verification Framework

Canonical examples are only useful when they stay correct. In a repository meant to guide coding assistants, an unverified example is worse than a missing one: it looks authoritative, it gets copied into new implementations, and it quietly spreads drift into generated code, prompts, manifests, and helper scripts.

This directory adds a structured verification layer for the repository so assistants and maintainers can distinguish between:

- examples that only exist as draft guidance
- examples that at least parse or type-check
- examples that have been mounted in a harness
- examples that have been run through a behavior check
- examples that are stable enough to treat as golden references

Verification improves assistant reliability because it gives the repo an explicit trust surface. A verified example is no longer just "present"; it has a known test target, a harness, an execution tier, and a confidence rating that can be surfaced in local tooling and CI.

## Verification Layers

- Repo integrity: required directories, manifests, templates, registry entries, and canonical references stay aligned.
- Prompt rules: prompt-first sequencing stays monotonic, suffix rules remain coherent, and prompt-file references resolve.
- Script verification: helper scripts keep producing valid output against real temp repos and broken fixtures.
- Example verification: canonical examples parse, import, and run through lightweight harnesses where feasible.
- Docker verification: runtime-heavy examples build and answer a minimal request without requiring every local toolchain.
- Data artifact verification: JSON and YAML examples load and retain required keys without forbidden placeholder patterns.

## Example Maturity Ladder

- `draft`
  The example is structurally useful but has no automated validation beyond file presence.
- `syntax-checked`
  The example parses or loads in a static verifier for its language or format.
- `smoke-verified`
  The example runs through a minimal harness or Docker request path and proves its primary surface works.
- `behavior-verified`
  The example has a small behavior assertion beyond boot, such as response shape, data writes, or route mounting.
- `golden`
  The example is stable, strongly verified, and preferred over nearby alternatives for generation.

## Directory Structure

- `verification/README.md`
  Philosophy, layers, and maturity model.
- `verification/example_registry.yaml`
  The authoritative registry for canonical examples, their verification level, target checks, Docker posture, harness, and confidence.
- `verification/stack_support_matrix.yaml`
  Stack-by-stack maturity view showing verified coverage and gaps.
- `verification/policies/`
  CI and policy documents for how verification tiers should run.
- `verification/unit/`
  Fast repo-integrity tests that do not need runtime stacks.
- `verification/scripts/`
  Tests for helper scripts and maintenance utilities.
- `verification/examples/`
  Stack-specific canonical example tests.
- `verification/scenarios/`
  Minimal harness projects or harness helpers used by example tests.
- `verification/fixtures/`
  Tiny valid and broken repos used to exercise script and policy checks.

## Execution Tiers

- Fast checks
  Repo integrity, prompt rules, manifest checks, alias-catalog checks, and repo-script checks.
- Medium checks
  Python example harnesses, data artifact tests, and Docker-backed API example smoke checks when enabled.
- Heavy checks
  Go and Rust runtime builds plus any future multi-container or cross-language harnesses.

## Design Constraints

- Local runs should not require every language toolchain.
- Docker-backed examples must stay small, official-image-based, and deterministic.
- Adding a new stack should mostly require one registry entry, one harness or parser test, and one matrix update.
- Assistants should prefer examples with higher verification level and higher confidence when more than one canonical option matches the task.
