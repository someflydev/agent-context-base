# ACB Payload Rules

This directory contains the machine-readable composition rules used to build repo-local `.acb/` payloads.

[`profile-rules.json`](profile-rules.json) defines:

- default doctrines and routers
- capability inference by archetype, manifest, and support service
- validation gates by archetype, stack, and capability

It is consumed by [`scripts/acb_payload.py`](../../scripts/acb_payload.py), not copied directly into generated repos.
