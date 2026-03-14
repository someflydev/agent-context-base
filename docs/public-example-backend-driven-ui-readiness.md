# Public Example Backend-Driven UI Readiness

This expansion adds a focused capability layer for future public example repos that need backend-driven interactive UIs with exact query semantics.

## Capability Overview

The repo now includes explicit guidance for:

- HTMX fragment patterns driven by backend state
- Tailwind-based server-rendered filter and result surfaces
- Plotly data endpoints derived from live filtered queries
- multi-select include and exclude filtering
- exact result counts and per-option facet counts
- Playwright verification of backend-generated UI behavior

## Why This Matters

Public examples become misleading when the interface looks interactive but counts, fragments, and charts do not share one backend truth. This capability layer keeps query correctness and UI behavior coupled.

## Future Repo Readiness

A future public example repo can now inherit:

- doctrine for query-state discipline, count correctness, and semantic UI verification
- workflows for adding faceted filters, include/exclude behavior, dynamic counts, Plotly views, and Playwright checks
- a cross-stack context pack for backend-driven HTMX, Tailwind, and Plotly work
- canonical FastAPI and Playwright examples that demonstrate the expected correctness posture

This prepares the base repo for a future public example that exposes backend APIs, renders HTMX and Tailwind views, drives Plotly charts, supports multi-faceted filtering, requires exact counts, and verifies behavior with Playwright without designing that repo here.

That future repo should still defer broad front-facing README, docs, and diagrams until the backend behavior, query semantics, and verification paths are real enough to document truthfully.
