# Proof-Transfer Benchmark

This package includes no-expected-proof challenge fixtures for reproducible Lean proof-transfer probes. They are deliberately separate from the original expected-proof corpus: Lean verification remains the oracle, but the package does not bundle gold proof bodies for these challenge fixtures.

## Challenge groups

| Group | Fixtures | Purpose |
| --- | ---: | --- |
| `challenge_v2_no_helper` | 3 | List proofs requiring local append/map helper lemma discovery. |
| `challenge_v3_generalization` | 4 | Theorem-generalization proofs requiring accumulator generalization and multi-helper proof plans. |
| `challenge_transfer` | 7 | All v2/v3 challenge fixtures. |
| `challenge_v4_count` | 4 | Count/list/tree fixtures covering occurrence counts, reverse, tree mirror/flatten, and successor-map-after-reverse. |
| `challenge_v5_attribution` | 4 | Simultaneous invariants and multi-helper composition fixtures designed to compare seeded, unseeded, and direct repair. |
| `challenge_v5_tree_tally` | 1 | The hard v5 tree/tally mirror fixture for attribution repeats. |
| `challenge_extended_transfer` | 15 | All v2/v3/v4/v5 challenge fixtures. |

## Reproducible commands

Seeded autocontext vs direct Pi repair-loop:

```bash
npm run benchmark:v3
npm run benchmark:v4
npm run benchmark:v5
```

Seeded autocontext vs unseeded isolated autocontext vs direct Pi repair-loop:

```bash
npm run benchmark:v5:attribution
```

Equivalent explicit harness invocations:

```bash
python3 harness/run_proof_transfer_benchmark.py \
  --fixture-group challenge_v5_attribution \
  --timeout 120 \
  --max-attempts 2 \
  --rounds 2

python3 harness/run_attribution_benchmark.py \
  --fixture-group challenge_v5_attribution \
  --timeout 120 \
  --max-attempts 2 \
  --rounds 2
```

The benchmark runners preserve the guardrails:

- provider: `pi`
- autocontext runtime: `uvx --python 3.12 --from autocontext==0.4.8 autoctx improve`
- `--no-pregenerate`
- `--structured-alternate-retry`
- synthetic hint candidates disabled
- Lean verification is the only success oracle

Outputs are written under a short temp directory by default, `the system temp directory (`pi-autocontext-lean-verify/...`)/...`, to avoid long Pi session paths when the package is loaded from npm temp `node_modules`. Set `AUTOCONTEXT_LEAN_VERIFY_RESULTS_ROOT` or pass `--run-root` / tool `runRoot` to override.

Artifacts include:

- `proof_transfer_benchmark_summary.json` / `proof_transfer_benchmark_report.md`
- `attribution_benchmark_summary.json` / `attribution_benchmark_report.md`
- method-specific stdout/stderr/command logs

## Local evidence snapshot

### v3 theorem-generalization repeated stability

| Method | Trials | Proofs | Success rate | Pi calls |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 3 | 12 / 12 | 100.0% | 12 |
| direct Pi repair-loop | 3 | 7 / 12 | 58.3% | 12 |

Hard-plus subset (`challenge_v3_tree_flatten_mirror`, `challenge_v3_map_rev_append_combined`): seeded autocontext `6 / 6`, direct Pi repair-loop `1 / 6`.

### v4 count/list/tree stability

| Method | Trials | Proofs | Success rate | Pi calls |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 3 × 4 | 12 / 12 | 100.0% | 12 |
| direct Pi repair-loop | 3 × 4 | 3 / 12 | 25.0% | 12 |
| unseeded isolated autocontext | 1 × 4 | 4 / 4 | 100.0% | 5 |

Interpretation: v4 shows the verifier-backed autocontext harness is robust compared with direct repair-loop, but it does not prove seed context is necessary because unseeded isolated solved all four.

### v5 attribution

| Method | Full v5 set | Hard tree/tally repeats |
| --- | ---: | ---: |
| seeded autocontext, v4 playbook | 4 / 4 | 3 / 3 |
| unseeded isolated autocontext | 3 / 4 | 1 / 3 |
| direct Pi repair-loop | 1 / 4 | 0 / 3 |

Interpretation: v5 is the strongest proof-transfer signal so far. The verifier-backed autocontext harness beats direct repair-loop overall, and seeded playbook context improves stability on the multi-helper tree/tally composition fixture.

## Guardrails

- Candidate supplies only `{{PROOF}}`.
- The theorem template is fixed.
- No `sorry`, `admit`, new axioms, `unsafe`, new imports, or theorem weakening.
- Lean verification is required before any success is counted.
- Challenge fixtures intentionally omit `expected_proof.lean`.
