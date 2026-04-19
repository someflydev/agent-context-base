# Plotly + HTMX + Tailwind Analytics Arc

## What This Arc Teaches
This arc reveals how to build fully testable, high-performance analytics applications without a heavy frontend framework. The core insight is treating Plotly as a declarative figure model built purely on the server. HTMX and Tailwind complement this by driving UI updates through fragment swaps and establishing a strict, language-agnostic CSS state contract. Dogfooding the canonical faker arc for fixtures ensures that the domain models are realistic and relational, proving the architecture scales correctly. This approach makes visualization logic reusable, deterministic, and verifiable across four distinct backends.

## The Three-Layer Model — Why It Matters
Separating data aggregation from figure-building and HTTP serialization is not just "good practice"—it fundamentally guarantees testability. It allows developers to unit test complex charting behavior independently from database queries or web server infrastructure. This model is extensively documented in `context/skills/plotly-figure-builder-design.md`. The most common violation to watch out for is combining aggregation logic directly into route handlers.

## Key Distinctions to Preserve

- Structure figure builders to return declarative data objects, not raw JSON strings; handlers manage the serialization.
- Separate aggregation and figure construction into discrete, testable layers.
- Confine HTMX fragment boundaries to the targeted panel; over-wide swaps obscure filter-state bugs.
- Treat Tailwind class definitions from `filter-panel-rendering-rules.md` as an explicit backend-to-frontend contract, not a cosmetic choice.
- Do not construct parallel fixture seeding systems; always dogfood the faker arc reference implementation.
- The Rust implementation uses `plotly.rs` and returns `serde_json::Value` from figure builders (documented deviation from the three-layer model).
- The Elixir implementation uses Phoenix controllers, NOT LiveView. HTMX + HEEx is the pattern here. LiveView is a valid but different approach.

## The Canonical Domain and Fixture Dogfooding
The analytics domain directly maps to TenantCore entities, driving realistic multi-tenant data challenges. Therefore, `generate_fixtures.py` delegates to the existing faker arc logic rather than inventing new generation tools. If fixtures become stale or the upstream data shapes change, update the faker arc first rather than breaking the integration.

## Navigation Shortcuts

- `docs/plotly-htmx-arc-overview.md` — The complete conceptual overview for this architecture.
- `examples/canonical-analytics/domain/parity-matrix.md` — The canonical cross-stack status and verification contract.
- `context/skills/plotly-figure-builder-design.md` — Deep dive on the three-layer pattern implementation.
- `context/doctrine/plotly-htmx-server-rendered-viz.md` — The absolute rules for building server-rendered visualizations.
- `examples/canonical-analytics/CATALOG.md` — High-level navigation to the specific backend implementations.