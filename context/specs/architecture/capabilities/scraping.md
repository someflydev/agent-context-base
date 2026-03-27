---
acb_origin: canonical
acb_source_path: context/specs/architecture/capabilities/scraping.md
acb_role: architecture
acb_capabilities: [scraping]
acb_version: 1
---

## Scraping Capability

Treat source fetch logic as hostile-to-stability by default. Architecture should isolate selectors, adapters, throttling, and normalization so source breakage does not spill into the whole system.
