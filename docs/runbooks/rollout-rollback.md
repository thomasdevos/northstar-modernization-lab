# Differential rollout and rollback

1. Run `make baseline`; stop if legacy differs from the golden master.
2. Run `make compare`; do not route traffic while any unexplained diff remains.
3. Review generated files in `evidence/runs/` and retain the decision.
4. Simulate rollout by selecting the replacement only after `make verify` passes.
5. Roll back by selecting the legacy batch path; input is replay-safe because duplicate settlement IDs are suppressed within a batch.

This lab has no live routing or external effects. In production, persist idempotency keys across process restarts before relying on replay.
