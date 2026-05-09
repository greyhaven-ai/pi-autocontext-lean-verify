# Proof-Transfer Benchmark

This package includes no-expected-proof challenge fixtures for reproducible Lean proof-transfer probes. They are deliberately separate from the original expected-proof corpus: Lean verification remains the oracle, but the package does not bundle gold proof bodies for these challenge fixtures.

## Challenge groups

| Group | Fixtures | Purpose |
| --- | ---: | --- |
| `challenge_v2_no_helper` | 3 | List proofs requiring local append/map helper lemma discovery. |
| `challenge_v3_generalization` | 4 | Theorem-generalization proofs requiring accumulator generalization and multi-helper proof plans. |
| `challenge_transfer` | 7 | All v2/v3 challenge fixtures. |

## Reproducible command

From a package checkout:

```bash
npm run benchmark:v3
```

Equivalent explicit harness invocation:

```bash
python3 harness/run_proof_transfer_benchmark.py \
  --fixture-group challenge_v3_generalization \
  --timeout 120 \
  --max-attempts 2 \
  --rounds 2
```

The benchmark runs two methods over the same fixed templates:

1. **seeded autocontext** via `run_playbook_transfer.py`
   - provider: `pi`
   - autocontext runtime: `uvx --python 3.12 --from autocontext==0.4.8 autoctx improve`
   - `--no-pregenerate`
   - `--structured-alternate-retry`
   - synthetic hint candidates disabled
   - seed playbook: `harness/playbooks/challenge_v2_no_helper_v1.md`
2. **direct Pi repair-loop** via `run_direct_baseline_benchmark.py`

Outputs are written under `harness/results/...`:

- `proof_transfer_benchmark_summary.json`
- `proof_transfer_benchmark_report.md`
- method-specific stdout/stderr/command logs

## Local evidence snapshot

The v3 repeated stability probe that motivated this packaged benchmark produced:

| Method | Trials | Proofs | Success rate | Pi calls |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 3 | 12 / 12 | 100.0% | 12 |
| direct Pi repair-loop | 3 | 7 / 12 | 58.3% | 12 |

Hard-plus subset (`challenge_v3_tree_flatten_mirror`, `challenge_v3_map_rev_append_combined`):

| Method | Hard-plus proofs |
| --- | ---: |
| seeded autocontext | 6 / 6 |
| direct Pi repair-loop | 1 / 6 |

Interpretation: seeded autocontext was stable on these theorem-generalization fixtures across three trials, while direct repair-loop remained unstable on the combined-helper proofs. This is evidence for a proof-transfer workflow, not a claim that autocontext is a standalone theorem prover.

## Guardrails

- Candidate supplies only `{{PROOF}}`.
- The theorem template is fixed.
- No `sorry`, `admit`, new axioms, `unsafe`, new imports, or theorem weakening.
- Lean verification is required before any success is counted.
- Challenge fixtures intentionally omit `expected_proof.lean`.
