# System Self-Explanation

`agent-context-base` is a prompt-first context system with light tooling, not a repo factory.

## How The Layers Work

- routers map normal language onto a small bundle
- doctrine holds durable rules
- workflows describe task sequences
- archetypes describe repo shape
- stacks describe concrete implementation details
- manifests package likely bundles and repo signals
- examples show preferred finished patterns
- templates provide starter scaffolds
- scripts validate integrity and help inspect the system

## Why This Repo Stays Small

The goal is predictability for Codex, Claude, and Gemini over long-lived usage. That means:

- fewer overlapping sources of truth
- machine-readable metadata where ranking or validation matters
- no repo-factory abstraction layer hiding simple file generation
- explicit extension paths instead of premature first-class support for every framework

## Extension Paths

The current first-class stacks remain FastAPI, TypeScript plus Hono plus Bun plus Drizzle plus TSX, Rust plus Axum, Go plus Echo plus templ, and Phoenix.

The repo also keeps these legible as extension paths without redesigning the architecture:

- Nim with Jester or HappyX
- Zig with Zap or Jetzig
- Scala with Tapir, http4s, or ZIO
- Clojure with Kit, next.jdbc, or Hiccup
- Kotlin with http4k or Exposed
- Crystal with Kemal or Avram
- OCaml with Dream, Caqti, or TyXML
- Dart with Dart Frog

Use the same pattern when promoting a new stack later: focused stack doc, aliases or signals, manifests only when the stack becomes common, and a canonical example only after the pattern stabilizes.
