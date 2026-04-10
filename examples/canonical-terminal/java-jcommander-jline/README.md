# TaskFlow Monitor - Java (JCommander + JLine)

Secondary Java example demonstrating a shell-style interaction model. JCommander
parses the top-level CLI and JLine powers the interactive `watch` REPL with
history, completion, and ANSI-friendly output.

## Stack

- CLI: JCommander
- Interactive shell: JLine 3
- Java 17+
- Maven

## Usage

```bash
mvn package -q
java -jar target/taskflow.jar list
java -jar target/taskflow.jar watch --no-repl
java -jar target/taskflow.jar watch
```

## Testing

```bash
mvn test -q
```

## Validation Approach

Use `java -jar target/taskflow.jar watch --no-repl` for CI smoke coverage.
JLine-driven interactive shell behavior is validated manually until PTY
automation is expanded for Java.

## Architecture

- `src/main/java/.../core/`: shared fixture-backed domain logic
- `src/main/java/.../cli/`: JCommander entrypoint and output formatting
- `src/main/java/.../repl/`: JLine shell loop, completion, and watch commands

## When to Use vs Flagship

- picocli + Lanterna: full-screen dashboard with panels
- JCommander + JLine: readline-style prompt with completion and command history
