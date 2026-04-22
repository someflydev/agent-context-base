# Terminal ↔ Web Parity

## Purpose

Helps future assistants and operators decide when a capability should be
exposed as a terminal tool, a web UI, or both.

**Status:** The terminal surface of this model is implemented in
`examples/canonical-terminal/`. The web surface uses the canonical-api
examples for the same domain.

## When Terminal is the Right Choice

### Automation and scripting pipelines

Terminal tools compose naturally with Unix pipes, cron, CI, and shell scripts.
Web UIs do not. If the primary consumer is another program or script, prefer
terminal.

### Operator-local inspection

When an operator needs to inspect local state (files, processes, queues)
without deploying a web service, terminal is lower friction. No port, no
browser, no auth.

### Latency-sensitive feedback loops

Terminal tools start faster and require no network round trip for display. For
fast interactive inspection, terminal is better.

### Secure/isolated environments

In air-gapped or locked-down environments, a terminal tool works where a
browser-accessible web UI cannot.

## When Web is the Right Choice

### Multi-user collaboration

Web UIs support concurrent users, sessions, and access control naturally.
Terminals are inherently single-user.

### Rich data visualization

Charts, graphs, and large tabular data with sorting and filtering UI are better
served by a browser with full CSS and JS capabilities.

### Public-facing interfaces

Public access without SSH or tool installation favors web.

### Mobile/non-terminal clients

Web works on mobile; terminal tools do not.

## When Both Are Right (Parity Pattern)

Build both when:

- The domain has both operator-local and collaborative consumption needs
- Automation (terminal) and exploration (web) are both first-class use cases
- The team has strong competence in both terminal and web tooling

Implementation pattern:

- shared domain core (no I/O, no rendering; pure logic)
- terminal surface: CLI + TUI (this arc)
- web surface: REST API + frontend (canonical-api examples)

Both surfaces import from the shared core. Neither reimplements domain logic.

## Parity Example: TaskFlow Monitor

The TaskFlow Monitor domain (job queue inspector) is a good parity candidate:

| Aspect | Terminal | Web |
|--------|----------|-----|
| Primary users | On-call engineers, CI automation | Managers, distributed teams |
| Deployment | CLI binary, no server | Deployed web service |
| Data source | Fixture files or local API | Remote API, database |
| Auth | OS-level (SSH, local user) | Web auth (cookie, JWT) |
| Real-time | Polling refresh or event replay | WebSockets or SSE |

The terminal examples in this arc implement the terminal surface. A web surface
for the same domain would use a backend-api archetype (FastAPI, Go Echo, and
similar) exposing the same job data via REST.

## Connecting Terminal and Web

When building both, consider:

- A shared local HTTP API (see `examples/canonical-terminal/docker/`) that the
  terminal tool connects to via `--api-url` and the web UI connects to.
- The terminal `--output json` flag makes terminal tool output consumable by
  web pipelines (webhook and curl-to-API patterns).
- PTY-based terminal output can be embedded in web UIs via xterm.js or similar
  as an advanced pattern; that is out of scope for this arc.

## See Also

- `context/archetypes/terminal-dual-mode.md`
- `context/archetypes/backend-api-service.md`
- `examples/canonical-terminal/DECISION_GUIDE.md`
- `examples/canonical-api/`
- `docs/terminal-validation-contract.md`
- `docs/ARCHITECTURE_MAP.md` (Terminal section)
