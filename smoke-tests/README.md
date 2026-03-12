# Smoke Tests

This directory explains the smoke-test role for future repos derived from this base.

## What Smoke Tests Are For

Smoke tests provide fast confidence that the simplest meaningful path still works:

- the process boots
- the main path responds
- obvious wiring breakage is caught quickly

## What This Base Repo Ships

This base repo ships smoke-test doctrine and starter guidance. It does not ship one-size-fits-all smoke tests for every future project.

Future repos should add smoke tests that match their own archetype and stack.

## How Smoke Tests Vary By Archetype

- backend API service: boot, health, one representative route
- CLI tool: one primary command and expected output shape
- data pipeline: one tiny input through one core transform
- local RAG system: one ingest-plus-query path
- Dokku-deployable service: one boot or readiness path that mirrors deployment expectations

## Pairing With Integration Tests

Significant features should usually pair smoke tests with minimal real-infra integration tests against the isolated test stack when they touch:

- databases
- caches
- queues
- search engines
- vector stores
- service boundaries

Smoke tests are necessary often. They are not enough for those boundaries on their own.

