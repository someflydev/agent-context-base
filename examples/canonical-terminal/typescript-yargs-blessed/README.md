# TaskFlow Monitor - TypeScript (Yargs + Blessed)

Secondary TypeScript example demonstrating Yargs for CLI parsing and Blessed
for a classic ncurses-style dashboard.

## Stack

- CLI: Yargs
- TUI: Blessed
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

## When to Use vs Flagship

- Commander + Ink: component-driven React model for terminal UIs
- Yargs + Blessed: widget-style, imperative terminal dashboards without React
