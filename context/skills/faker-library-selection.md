# Faker Library Selection

Use this skill to choose the faker stack before implementing generation code.

## Decision Table

| If the request is about | Then load or choose | Notes |
| --- | --- | --- |
| Python relational generator | `context/stacks/faker-python.yaml` -> Faker first | Use Mimesis when custom providers or schema-style generation matter more than ecosystem ubiquity. |
| JavaScript or Node.js CLI generator | `context/stacks/faker-javascript.yaml` -> `@faker-js/faker` first | Add Chance when weighted picks or custom probability control are central. |
| Go relational generator | `context/stacks/faker-go.yaml` -> gofakeit first | Use `go-faker/faker` only when tag-driven struct population is the teaching contrast. |
| Rust typed generator | `context/stacks/faker-rust.yaml` -> fake | Keep the graph layer explicit; fake-rs already covers the main atomic generation styles. |
| Java JVM generator | `context/stacks/faker-java.yaml` -> Datafaker | Do not invent a second primary JVM faker unless the task demands legacy comparison. |
| Kotlin generator | `context/stacks/faker-kotlin.yaml` -> kotlin-faker first | Use Datafaker when JVM interop or Java-team familiarity is the constraint. |
| Scala generator | `context/stacks/faker-scala.yaml` -> scala-faker only if maintenance is acceptable | Otherwise use Datafaker and state that Scala's native faker ecosystem is thin. |
| Ruby generator | `context/stacks/faker-ruby.yaml` -> faker | Use ffaker when speed or legacy compatibility matters more than category breadth. |
| PHP generator | `context/stacks/faker-php.yaml` -> FakerPHP/Faker for imperative generation | Add Alice when the task benefits from declarative relational fixture graphs. |
| Elixir generator | `context/stacks/faker-elixir.yaml` -> Faker | Add ExMachina when factory declarations and Ecto-oriented graph assembly improve clarity. |

## Routing Rules

| Signal | Action |
| --- | --- |
| Atomic field generation only | Use the primary faker library alone. |
| Full relational graph generation | Load `context/skills/synthetic-dataset-design.md` and keep the graph layer explicit above faker. |
| Locale-sensitive output | Prefer the library with stronger locale coverage and document the locale choice. |
| SQL seed or fixture-oriented output | Consider graph or factory libraries only if they improve readability without hiding ordering rules. |
| Ecosystem is thin or maintenance is uncertain | Name the caveat directly and prefer the pragmatic fallback instead of pretending parity exists. |

## Avoid

- treating faker choice as the full dataset design
- adding a graph library when explicit orchestration is clearer
- ignoring locale support when realistic names or addresses matter
- describing Scala as equally deep as Python or JavaScript
