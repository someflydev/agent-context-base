## Multi-Source Sync Platform Intent

The product coordinates recurring sync work across multiple sources, checkpoints, and downstream consumers. Correctness depends on orchestration behavior, not only one isolated fetch path.

Specs should describe which sync boundaries are authoritative, how progress is resumed, and what consistency the platform promises after interruption.
