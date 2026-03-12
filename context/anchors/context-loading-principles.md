# Context Loading Principles Anchor

- load one router, one workflow, one archetype, and one primary example first
- use manifests to assemble bundles instead of hand-collecting many files
- open optional context only when the task or repo signals activate it
- use `python scripts/preview_context_bundle.py <manifest> --show-weights --show-anchors`
- do not scan `context/`, `examples/`, or `manifests/` wholesale
