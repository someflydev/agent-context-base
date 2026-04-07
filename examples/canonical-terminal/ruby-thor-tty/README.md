# TaskFlow Monitor - Ruby (Thor + TTY::Prompt)

Flagship Ruby terminal example. Guided interactive CLI inspector using
TTY::Prompt menus and selections. CLI structure via Thor.

## Stack

- CLI: Thor
- Interactive mode: TTY::Prompt
- Output formatting: TTY::Table + TTY::Color
- Ruby 3.2+

## Usage

```bash
bundle install
bin/taskflow list
bin/taskflow list --status failed --output json
bin/taskflow inspect job-001
bin/taskflow stats --output json
bin/taskflow watch
bin/taskflow watch --no-interactive
```

## Testing

```bash
bundle exec ruby tests/smoke/test_cli_smoke.rb
bundle exec ruby tests/unit/test_core.rb
```

## Ruby Terminal Philosophy

Ruby shines at guided interactive workflows: prompts, menus, confirmations, and
wizard-like inspection flows. This example deliberately uses a prompt-driven
inspector instead of forcing a full-screen TUI.

## When to Use

Operator tools, guided remediation workflows, interactive installers, and
configuration wizards where prompt-driven UX is the main goal.
