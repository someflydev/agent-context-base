# Canonical Example Selection

Use this skill to choose the best example surface without mixing conflicting patterns.

## Procedure

1. confirm the active workflow
2. confirm the active stack and archetype
3. load doctrine or workflow invariants first when the task is still stack-neutral
4. choose one example category that matches the task
5. prefer the example closest to the implementation surface

## Priority

- exact stack plus exact task match
- exact stack plus exact task match with the highest verification level
- higher verification confidence when stack and task relevance tie
- exact task match with neutral stack assumptions
- nearest archetype match

If no stack-matching canonical example exists:

- say that explicitly
- fall back to the relevant invariant docs
- use the closest honestly verified example in the same stack only as a fallback, not as a mislabeled canonical match

## Avoid

- combining two examples with different structural assumptions
- treating templates as if they were canonical examples
- treating language-agnostic doctrine as if it were a stack-specific implementation
- treating a Python example as the default answer for a Go, Rust, TypeScript, Elixir, Nim, Zig, or Crystal request
- treating `examples/canonical-cli/` as equivalent to `examples/canonical-terminal/` when the task explicitly targets CLI tooling, TUI, or dual-mode patterns — use `context/skills/terminal-example-selection.md` for terminal tasks
- creating a new example when the pattern is still unstable
- preferring a lower-verified example when a higher-verified nearby option exists

## See Also

- `terminal-example-selection.md` — for CLI, TUI, and dual-mode terminal examples
