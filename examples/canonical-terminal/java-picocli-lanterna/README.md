# TaskFlow Monitor - Java (picocli + Lanterna)

Flagship Java dual-mode terminal example. picocli provides the command surface
and Lanterna provides a pure-Java text UI for interactive inspection.

## Stack

- CLI: picocli
- TUI: Lanterna
- Java 17+
- Maven

## Usage

```bash
mvn package -q
java -jar target/taskflow.jar list
java -jar target/taskflow.jar watch --no-tui
java -jar target/taskflow.jar watch
```

## Testing

```bash
mvn test -q
```

## Validation Approach

Use `java -jar target/taskflow.jar watch --no-tui` for CI smoke coverage.
Full-screen Lanterna interaction is currently validated manually per
`docs/terminal-validation-contract.md`; PTY automation is a Phase 2 follow-up.

## Architecture

- `src/main/java/.../core/`: shared fixture-backed domain logic
- `src/main/java/.../cli/`: picocli command tree and output formatting
- `src/main/java/.../tui/`: Lanterna application and screen components

## When to Use

Use picocli + Lanterna when a JVM team needs both a scriptable CLI and a
dashboard-style text GUI without leaving Java.
