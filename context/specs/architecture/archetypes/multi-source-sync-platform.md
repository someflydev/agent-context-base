## Multi-Source Sync Architecture

Sync orchestration, source adapters, checkpoint persistence, and downstream emission should remain explicit seams. The coordinator may own timing and progression, but each source adapter should keep its own normalization and failure policy narrow.

Do not hide multi-source coordination inside one giant job script that cannot be resumed or validated incrementally.
