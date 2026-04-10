# TaskFlow Monitor - Ruby (Clamp + TTY::Reader)

Secondary Ruby example. Minimal CLI via Clamp. Raw keyboard input and a
line-oriented interactive pager via TTY::Reader.

## Stack

- CLI: Clamp
- Interactive mode: TTY::Reader
- Output styling: TTY::Color
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

## Architecture

- `lib/taskflow/core.rb`: shared fixture-backed job loading and stats logic
- `lib/taskflow/cli.rb`: Clamp command definitions and output formatting
- `lib/taskflow/watch.rb`: TTY::Reader-driven watch loop

## When to Use vs Flagship

- `Thor + TTY::Prompt`: guided menus, select dialogs, wizard flows
- `Clamp + TTY::Reader`: simpler CLI, raw keystroke handling, custom key-driven
  pager
