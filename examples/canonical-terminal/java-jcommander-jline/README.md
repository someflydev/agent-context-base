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

## When to Use vs Flagship

- picocli + Lanterna: full-screen dashboard with panels
- JCommander + JLine: readline-style prompt with completion and command history
