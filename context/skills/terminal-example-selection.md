# Terminal Example Selection

Use this skill to choose the right terminal canonical example for CLI, TUI, or dual-mode work.

## Procedure

1. identify the terminal tier from task signals:
   - **Tier 1 CLI**: subcommands, flags, `--output json`, scriptable, headless
   - **Tier 2 TUI**: full-screen keyboard-driven UI, rich rendering, interactive
   - **Tier 3 dual-mode**: shared core, both CLI and TUI surfaces via `--interactive`
2. identify the language and whether the task should start from a flagship or secondary example
3. prefer flagship examples for new work:
   - `python-typer-textual`
   - `rust-clap-ratatui`
   - `go-cobra-bubbletea`
   - `typescript-commander-ink`
   - `java-picocli-lanterna`
   - `ruby-thor-tty`
   - `elixir-optimus-ratatouille`
4. use a secondary example only when the stack explicitly matches the secondary library:
   - `python-click-blessed`
   - `rust-argh-tui-realm`
   - `go-urfave-tview`
   - `typescript-yargs-blessed`
   - `java-jcommander-jline`
   - `ruby-clamp-tty`
   - `elixir-optionparser-owl`
5. load `examples/canonical-terminal/DECISION_GUIDE.md` for language-vs-tier guidance before recommending a stack or example
6. confirm the example exists in `examples/canonical-terminal/CATALOG.md` before recommending it
7. if no exact-language match exists for the requested tier, state the gap explicitly and do not silently substitute a different language
8. prefer implemented examples over stubs; if you must point to a stub, flag that status explicitly

## Priority

- exact language plus exact tier, flagship first
- exact language plus exact tier, secondary only when the library match is explicit
- exact language plus adjacent tier, with the mismatch stated
- same language family with the gap stated clearly

## Good Triggers

- "add a terminal example for Go"
- "which Rust TUI example should I follow"
- "what is the canonical reference for Elixir CLIs"
- "how do I validate a dual-mode operator console"
- "which example matches a Java terminal dashboard"
- "what should I use for a Ruby guided terminal workflow"

## Avoid

- selecting `examples/canonical-cli/` for a terminal tooling task
- mixing CLI, TUI, and dual-mode tiers silently
- using a web, API, or storage example for a terminal task
- presenting stubs as if they were implemented canonical references
- substituting a different language without stating the gap

## Reference Files

- `examples/canonical-terminal/CATALOG.md`
- `examples/canonical-terminal/DECISION_GUIDE.md`
- `context/archetypes/terminal-tui.md`
- `context/archetypes/terminal-dual-mode.md`
- `context/archetypes/cli-tool.md`
