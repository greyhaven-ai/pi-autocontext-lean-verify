# Formal Proof Package Domain Model

Bounded context: **Formal Proof Package Validation**.

The package wraps the external Lean pilot harness. Its job is not to prove theorems directly; it orchestrates verifier-backed proof experiments and reports only Lean-checked outcomes.

## Ubiquitous language

- **Harness root**: directory containing `benchmark_manifest.json`, `run_playbook_transfer.py`, fixtures, and result artifacts.
- **Fixture**: one fixed Lean theorem template plus one expected proof used only for harness sanity checks.
- **Fixture group**: named, curated list of fixture ids exposed through package UX.
- **Mode**: named runner flag bundle for proof-transfer behavior.
- **Setup**: package readiness check consisting of preflight plus a minimal Lean smoke proof.
- **Validation matrix**: compact evidence table linking package claims to durable result artifacts.
- **Negative control**: fixture where generated synthetic hint candidates should fail Lean and be discarded before Pi fallback.
- **Lean oracle**: the only source of proof success; LLM/Pi text never counts without Lean verification.

## Domain rules

1. Fixture groups must reference only fixture ids present in the harness manifest.
2. `combined` is exactly `broader` followed by `heldout`.
3. `negative_controls` must exercise hint rejection, not just fixture variety.
4. Package documentation must describe setup, fixture groups, and negative-control recovery without implying autocontext itself proves the theorem.
5. Package distribution must include only runtime package resources, not result artifacts or local test outputs.
6. Validation claims must point to durable result artifacts under `results/`.

## DRY boundaries

- Fixture group membership has one source of truth: `fixture_groups.json`.
- Extension preflight, package docs, and validation tests must derive or verify against that source.
- Result metrics remain in `results/*/summary.json`; docs summarize, not reimplement, those artifacts.
