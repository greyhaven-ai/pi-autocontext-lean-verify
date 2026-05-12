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
| `challenge_v9_composition_gradient` | 6 | Composition-gradient fixtures splitting keep/drop partition-through-mirror into scalar and paired length/sum obligations. |
| `challenge_v10_stats_reification` | 6 | StatsAcc-reification fixtures isolating tuple normalization, metric extensionality, count metrics, and stats equality from metric hypotheses. |
| `challenge_v11_metric_composition` | 6 | Metric-composition fixtures combining keep/drop metric bundles with statsAcc extensionality boundaries. |
| `challenge_v12_simultaneous_metrics` | 7 | Simultaneous-metric fixtures splitting keep/drop count-only, length-only, sum-only, pair, and triple metric bundles. |
| `challenge_extended_transfer` | 52 | All v2/v3/v4/v5/v6/v7/v8/v9/v10/v11/v12 challenge fixtures. |

## Reproducible commands

Seeded autocontext vs direct Pi repair-loop:

```bash
npm run benchmark:v3
npm run benchmark:v4
npm run benchmark:v5
npm run benchmark:v6
npm run benchmark:v7
npm run benchmark:v8
npm run benchmark:v9
npm run benchmark:v10
npm run benchmark:v11
npm run benchmark:v12
```

Seeded autocontext vs unseeded isolated autocontext vs direct Pi repair-loop:

```bash
npm run benchmark:v5:attribution
npm run benchmark:v6
npm run benchmark:v7
npm run benchmark:v8
npm run benchmark:v9
npm run benchmark:v10
npm run benchmark:v11
npm run benchmark:v12
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
npm run benchmark:v9
npm run benchmark:v10
npm run benchmark:v11
npm run benchmark:v12
```

Or through Pi with `action="attribution"` and the corresponding `fixtureGroup`.


## v8 diagnostic suite

Version `0.1.10` adds `challenge_v8_diagnostics`, a four-fixture suite that decomposes the v7 partition-heavy accumulator frontier into smaller theorem obligations:

- raw `statsAcc` invariance through tree mirror, before partitioning;
- keep-side partition stats through tree mirror;
- drop-side partition stats through tree mirror;
- list-only partition/reassembly equivalence for `statsAcc`.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first two controlled attribution probes solved seeded `6/8`, unseeded `1/8`, and direct `0/8`: raw tree/mirror stats and list-only reassembly are stable for seeded autocontext, while keep/drop partition-through-mirror remains stochastic. This indicates the v7 instability is mainly compositional.


## v9 composition-gradient suite

Version `0.1.10` adds `challenge_v9_composition_gradient`, a six-fixture suite focused on the stochastic keep/drop partition-through-mirror components:

- keep-side length through tree mirror;
- keep-side sum through tree mirror;
- paired keep-side length+sum through tree mirror;
- drop-side length through tree mirror;
- drop-side sum through tree mirror;
- paired drop-side length+sum through tree mirror.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `6/6`, unseeded `1/6`, and direct `0/6`, indicating length/sum partition-through-mirror obligations are learnable with seed context and the remaining frontier is likely `statsAcc` triple reification/composition.


## v10 stats-reification suite

Version `0.1.10` adds `challenge_v10_stats_reification`, a six-fixture suite focused on the `statsAcc` triple reification frontier:

- generic reification of `statsAcc` into `(count, length, sum)` metrics;
- extensionality of `statsAcc` from equal count/length/sum metrics;
- keep-side and drop-side count metrics through tree mirror;
- keep-side and drop-side `statsAcc` equality from already-proved metric equalities.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `6/6`, unseeded `3/6`, and direct `1/6`: unseeded can solve core reification/count metrics, but seed context is needed for extensionality and metric-hypothesis application.


## v11 metric-composition suite

Version `0.1.10` adds `challenge_v11_metric_composition`, a six-fixture suite bridging metric proofs and `statsAcc` equality without asking the model to synthesize the full v7/v8 theorem outright:

- keep-side and drop-side metric bundles through tree mirror;
- keep-side and drop-side `statsAcc` equality from bundled metric proofs;
- combined keep/drop metric bundles;
- combined keep/drop stats equality from metric bundles.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `5/6`, unseeded `0/6`, and direct `1/6`, with the only seeded miss on the combined keep/drop metric-bundle proof.


## v12 simultaneous-metric suite

Version `0.1.10` adds `challenge_v12_simultaneous_metrics`, a seven-fixture suite isolating the combined keep/drop metric-bundle proof:

- simultaneous keep/drop count metrics;
- simultaneous keep/drop length metrics;
- simultaneous keep/drop sum metrics;
- simultaneous count+length, count+sum, and length+sum metric pairs;
- simultaneous count+length+sum metric bundle.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `6/7`, unseeded `0/7`, and direct `0/7`: all one-metric and two-metric simultaneous bundles solved seeded, while the full count+length+sum bundle failed. Isolated repeats of that triple bundle show seeded stochasticity (`1/3` across full-suite plus isolated observations), not theorem falsehood.
