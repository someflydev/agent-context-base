# Terminal Stack Decision Guide

Use this guide to choose the right language and library combination for a
terminal tooling project.

## Quick Decision Tree

1. What is your primary language constraint?
   -> Python: see Python section
   -> Rust: see Rust section
   -> Go: see Go section
   -> TypeScript/Node: see TypeScript section
   -> Java/JVM: see Java section
   -> Ruby: see Ruby section
   -> Elixir/BEAM: see Elixir section
   -> No constraint: see Cross-Language Comparison

2. What interaction model do you need?
   -> Scripting/automation only (no interactive UI): any CLI-tier stack
   -> Guided prompts / menus / wizards: Ruby Thor+TTY::Prompt or Python Typer
   -> Full-screen dashboard / table / panels: Python Textual, Rust ratatui,
      Go Bubble Tea, TypeScript Ink, Java Lanterna, Elixir Ratatouille
   -> Shell-style REPL with readline: Java JCommander+JLine
   -> Light colored output / simple pager: Click+Blessed, Clamp+TTY::Reader,
      Yargs+Blessed, OptionParser+Owl

---

## Python

| Need | Stack |
|------|-------|
| Full-screen TUI + CLI, modern async | Typer + Textual |
| Light CLI + colored output + simple keys | Click + Blessed |
| Existing Click app, add light interaction | Click + Blessed |
| Existing FastAPI/async project | Typer + Textual (async-native) |

Textual vs Blessed:
- Textual: CSS-styled widgets, component model, async, web export potential
- Blessed: line-oriented, simpler, more Unix-y, lighter weight

---

## Rust

| Need | Stack |
|------|-------|
| High-performance, full-screen TUI, max control | clap + ratatui |
| Component/subscription TUI (Elm-style), simpler CLI | argh + tui-realm |
| Existing clap project, adding TUI | clap + ratatui |

ratatui vs tui-realm:
- ratatui: raw draw loop, maximum control, most community momentum
- tui-realm: higher abstraction, Elm-like, easier to extend large TUIs

---

## Go

| Need | Stack |
|------|-------|
| kubectl/git-style command tree + functional TUI | Cobra + Bubble Tea |
| Simple CLI + widget-centric TUI (tables, forms) | urfave/cli + tview |
| Large command tree (10+ subcommands) | Cobra + Bubble Tea |

Bubble Tea vs tview:
- Bubble Tea: functional/immutable model, clean composition, lipgloss styling
- tview: imperative widgets, rich built-ins (tables, forms, trees), less boilerplate

---

## TypeScript

| Need | Stack |
|------|-------|
| React devs, component-style TUI, modern tooling | Commander + Ink |
| Classic ncurses-style TUI, no React | Yargs + Blessed |
| Complex command parsing with middleware | Yargs (either TUI lib) |

Ink vs Blessed:
- Ink: React paradigm, JSX, clean composition, good for React-familiar teams
- Blessed: ncurses-style, larger widget set, no React overhead

---

## Java

| Need | Stack |
|------|-------|
| Full-screen TUI panels + structured CLI | picocli + Lanterna |
| Shell REPL + readline + tab completion | JCommander + JLine |
| Annotation-heavy enterprise CLI | picocli (either TUI lib) |

Lanterna vs JLine:
- Lanterna: full text-GUI (panels, dialogs, forms) - real TUI
- JLine: interactive console input (readline, completion) - REPL, not panels

---

## Ruby

Ruby terminal tooling note:
Ruby's ecosystem is optimized for guided interactive CLIs and prompt-driven
workflows. It does NOT have a production-grade full-screen TUI framework
equivalent to ratatui or Textual. For dashboard-style panels:
-> prefer Python (Textual), Rust (ratatui), or Go (Bubble Tea)

| Need | Stack |
|------|-------|
| Guided menus, selection dialogs, wizards | Thor + TTY::Prompt |
| Simple CLI + raw keystroke pager | Clamp + TTY::Reader |
| Existing Thor app, add interactive prompts | Thor + TTY::Prompt |

---

## Elixir

| Need | Stack |
|------|-------|
| Full-screen TUI + BEAM supervision + OTP patterns | Optimus + Ratatouille |
| Rich CLI output (tables, spinners, color), no TUI | OptionParser + Owl |
| Mix task with styled output | OptionParser + Owl |
| Process-supervised live data feed -> terminal | Optimus + Ratatouille + GenServer |

BEAM guidance:
Use GenServer/supervision when you have live data, async updates, or concurrent
state management needs. For a static fixture-backed tool, simple module functions
are sufficient.

---

## Cross-Language Comparison

| Aspect | Python | Rust | Go | TypeScript | Java | Ruby | Elixir |
|--------|--------|------|----|------------|------|------|--------|
| Full-screen TUI | Textual | ratatui | Bubble Tea | Ink | Lanterna | limited | Ratatouille |
| CLI builder | Typer/Click | clap/argh | Cobra/urfave | Commander/Yargs | picocli/JCommander | Thor/Clamp | Optimus/OptionParser |
| Startup time | medium | fast | fast | medium | slow | medium | medium |
| Concurrency model | async | OS threads | goroutines | event loop | JVM threads | GIL | BEAM actors |
| Ecosystem maturity | high | high | high | high | high | medium | medium |
| Best for | operator consoles, Python shops | perf-critical tools | devops CLIs | Node/devtools | JVM enterprise | guided workflows | BEAM process monitors |

## Common Anti-Patterns

- Building full-screen TUI in Ruby when Rust/Python would be more appropriate
- Using Yargs+Blessed when you actually want React component composition (use Ink)
- Skipping `--no-tui` flag in a TUI tool (breaks CI)
- Duplicating domain logic in CLI and TUI surfaces (use shared `core/`)
- Network calls in smoke tests (use `fixtures/`)

## See Also

- `context/archetypes/terminal-dual-mode.md`
- `context/archetypes/terminal-tui.md`
- `context/doctrine/terminal-ux-first-class.md`
- `context/router/stack-router.md` (terminal stacks section)
- `CATALOG.md` (this directory)
