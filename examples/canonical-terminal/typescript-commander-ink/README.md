# TaskFlow Monitor - TypeScript (Commander + Ink)

Flagship TypeScript dual-mode terminal example. Commander provides the command
surface and Ink renders a React-style dashboard for interactive inspection.

## Stack

- CLI: Commander
- TUI: Ink + React
- TypeScript 5
- Node.js 20+

## Usage

```bash
npm install
npm run build
node dist/cli/index.js list
node dist/cli/index.js watch --no-tui
node dist/cli/index.js watch
```

## Testing

```bash
npm test
```

## Architecture

- `src/core/`: fixture loading, filtering, and stats
- `src/cli/`: Commander command surface and assertable output helpers
- `src/tui/`: Ink components and keyboard-driven dashboard
- `tests/smoke/`: CLI smoke tests that run without a TTY

## When to Use

Use Commander + Ink when a TypeScript team wants a modern, component-based
terminal UI without giving up a scriptable CLI surface.
