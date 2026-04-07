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

## When to Use

Use picocli + Lanterna when a JVM team needs both a scriptable CLI and a
dashboard-style text GUI without leaving Java.
