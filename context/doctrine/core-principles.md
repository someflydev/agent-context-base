# Core Principles

These principles anchor the rest of the repo.

## Build The Smallest Useful Thing

Prefer a strong v1 over a speculative v3. Add the next layer only when a real task needs it.

## Separate Stable Rules From Task Playbooks

- doctrine explains enduring rules
- workflows explain how to execute a task
- stacks explain implementation surfaces
- archetypes explain project shape
- examples show preferred patterns
- templates give starter scaffolds

Do not collapse these layers into one file.

## Optimize For Real Work

This base should help with active coding sessions, not just documentation elegance. Every file should help a human or assistant make a concrete decision.

## Favor Inference Over Internal Vocabulary

Users should be able to say normal things like "add an endpoint" or "bootstrap a repo". Routing should map that language onto the right files.

## Prefer Canonical Patterns

Reuse a clear canonical pattern before inventing a hybrid. If no canonical pattern exists, make the smallest new pattern that still fits doctrine and stack guidance.

## Test Significant Boundaries Properly

Smoke tests are necessary often, but they are not enough when a feature touches:

- databases
- caches
- queues
- search engines
- cross-service calls

Those changes usually need minimal real-infra integration tests against isolated test infrastructure.

## Keep Future Repos Lightweight

This repo is a base, not a permanent meta-platform. Future projects should copy the relevant parts and then specialize locally.

## Let Front-Facing Docs Follow Implementation

In new derived repos, defer substantial root `README.md`, `docs/`, and Mermaid architecture docs until the implementation has enough real structure to describe honestly.
