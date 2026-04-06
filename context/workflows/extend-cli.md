# Extend CLI

Use this workflow when adding commands, flags, or output modes to a CLI tool.

## Preconditions

- the existing command surface is understood
- expected input and output shape are clear

## Sequence

1. place the new command within the existing command tree
2. keep flags and help text explicit
3. add smoke coverage for the main invocation
4. add integration coverage if the command touches real storage, network, or search boundaries
5. document the operator-facing usage if the command is important

## Outputs

- new or updated command path
- smoke test
- integration test when needed

## Related Docs

- `context/archetypes/cli-tool.md`
- `examples/canonical-cli/README.md`

## Common Pitfalls

- adding hidden side effects to a command
- unclear defaults
- unstructured output that breaks downstream use

## See Also

For full-screen TUI or dual-mode CLI+TUI tools:

- `context/workflows/add-terminal-example.md`
- `context/archetypes/terminal-tui.md`
- `context/archetypes/terminal-dual-mode.md`
- `context/doctrine/terminal-ux-first-class.md`
