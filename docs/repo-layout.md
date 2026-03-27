# Repo Layout

The repository is organized so assistants can route first, compose or generate `.acb/` payloads, and verify that the system still matches its own documentation.

| Path | Role |
| --- | --- |
| [`README.md`](../README.md) | Front door for humans and assistants. |
| [`AGENT.md`](../AGENT.md), [`CLAUDE.md`](../CLAUDE.md) | Minimal assistant boot docs. |
| [`context/specs/`](../context/specs/README.md) | Canonical product, architecture, agent, and evolution modules. |
| [`context/validation/`](../context/validation/README.md) | Canonical validation modules. |
| [`context/acb/`](../context/acb/README.md) | Payload composition rules. |
| `context/router/`, `context/doctrine/`, `context/workflows/`, `context/stacks/`, `context/archetypes/`, `context/anchors/`, `context/skills/` | Broader routing and support guidance used by manifests and startup flows. |
| [`manifests/`](../manifests) | Machine-readable context bundles and generation defaults. |
| [`examples/`](../examples/README.md) | Canonical examples. |
| [`templates/`](../templates/README.md) | Bootstrap scaffolds. |
| [`scripts/`](../scripts/README.md) | Generation, composition, inspection, and verification tools. |
| [`verification/`](../verification/README.md) | Verification suites and fixtures. |
