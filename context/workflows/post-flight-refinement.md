# Post-Flight Refinement

Purpose: add stage-2 tightening after a first implementation pass.

Sequence:

1. inspect the first-pass outputs
2. identify drift, missing tests, weak examples, or overloaded docs
3. refine the smallest layer that fixes the issue
4. do not rebuild the architecture from scratch unless a core contradiction exists

Pitfalls:

- treating refinement as a blank-sheet rewrite
- expanding context instead of tightening it
