# Context Integrity Anchor

- run `python scripts/validate_context.py` before trusting metadata-heavy changes
- run `python scripts/validate_manifests.py` when touching only manifest logic
- use `python scripts/preview_context_bundle.py <manifest> --show-weights --show-anchors`
- use `python scripts/pattern_diff.py <left> <right>` to compare a candidate against a canonical pattern
- keep prompt numbering monotonic in `examples/canonical-prompts/` and `templates/prompt-first/`
