# Scala: Tapir + http4s + ZIO

Use this pack for Scala backend services that need typed endpoint contracts, explicit HTTP wiring, and structured effect management.

## Typical Repo Surface

- `build.sbt`
- `project/build.properties`
- `src/main/scala/`
- `src/test/scala/`
- `modules/http/`
- `modules/domain/`
- `modules/services/`

## Common Change Surfaces

- Tapir endpoint definitions
- http4s route composition and middleware
- ZIO service layers and effect boundaries
- JSON codec derivation
- server startup wiring

## Testing Expectations

- keep source examples structure-verified when they are teaching snippets
- use Docker-backed smoke verification for runnable services so local Scala tooling stays optional
- verify one JSON endpoint, one fragment endpoint, and one chart-data endpoint when the stack is used for interactive backends

## Common Assistant Mistakes

- collapsing Tapir contracts and business logic into one large `run` block
- treating http4s as incidental and hiding the actual route composition surface
- returning untyped map-like payloads where Tapir plus ZIO codecs should make the contract explicit
