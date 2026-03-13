# Zig Zap Jetzig Runtime Example

Minimal runtime bundle for Docker-backed verification of the Zig Zap plus Jetzig canonical API surface.

Endpoints:

- `/healthz`
- `/api/reports/@tenantId`
- `/fragments/report-card/@tenantId`
- `/data/chart/@metric`

Notes:

- the runtime bundle uses Zap for the executable transport surface
- the companion Jetzig fragment example stays source-verified and demonstrates the preferred view pattern
- the Dockerfile fetches the pinned Zap dependency inside the container so host Zig tooling is not required

Verification level: smoke-verified  
Harness: zig_zap_jetzig_min_app  
Last verified by: verification/examples/zig/test_zig_zap_jetzig_examples.py
