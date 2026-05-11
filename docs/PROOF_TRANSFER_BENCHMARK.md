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
| `challenge_v6_frontier` | 4 | Frontier fixtures covering multi-accumulator reverse invariants, nested tree partition stats, successor-map reverse count/sum, and mutual tree stats. |
| `challenge_v7_frontier` | 4 | Frontier-plus fixtures combining partition/tree mirror composition with stats accumulator normalization. |
| `challenge_v8_diagnostics` | 4 | Diagnostic fixtures isolating the v7 partition-heavy accumulator frontier into smaller components. |
| `challenge_extended_transfer` | 27 | All v2/v3/v4/v5/v6/v7/v8 challenge fixtures. |

## Reproducible commands

Seeded autocontext vs direct Pi repair-loop:

```bash
npm run benchmark:v3
npm run benchmark:v4
npm run benchmark:v5
npm run benchmark:v6
npm run benchmark:v7
npm run benchmark:v8
```

Seeded autocontext vs unseeded isolated autocontext vs direct Pi repair-loop:

```bash
npm run benchmark:v5:attribution
npm run benchmark:v6
npm run benchmark:v7
npm run benchmark:v8
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


## v6/v7 frontier suites

Version `0.1.9` adds two frontier attribution groups:

- `challenge_v6_frontier`: seeded `4/4`, unseeded `3/4`, direct `2/4` in the development probe.
- `challenge_v7_frontier`: seeded `2/4`, unseeded `0/4`, direct `0/4`; the two seeded-failed partition-heavy fixtures repeated at `0/6`.

Run from a checkout with:

```bash
npm run benchmark:v6
npm run benchmark:v7
npm run benchmark:v8
```

Or through Pi with `action="attribution"` and the corresponding `fixtureGroup`.


## v8 diagnostic suite

The source tree after `0.1.9` adds `challenge_v8_diagnostics`, a four-fixture suite that decomposes the v7 partition-heavy accumulator frontier into smaller theorem obligations:

- raw `statsAcc` invariance through tree mirror, before partitioning;
- keep-side partition stats through tree mirror;
- drop-side partition stats through tree mirror;
- list-only partition/reassembly equivalence for `statsAcc`.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first two controlled attribution probes solved seeded `6/8`, unseeded `1/8`, and direct `0/8`: raw tree/mirror stats and list-only reassembly are stable for seeded autocontext, while keep/drop partition-through-mirror remains stochastic. This indicates the v7 instability is mainly compositional.
