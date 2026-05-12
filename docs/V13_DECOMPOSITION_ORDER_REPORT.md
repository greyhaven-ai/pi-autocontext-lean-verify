# V13 Decomposition/Order Fixtures

`challenge_v13_decomposition_order` is a source follow-up to the v12 simultaneous-metric frontier. V12 showed that seeded autocontext handles every one-metric and two-metric simultaneous keep/drop bundle, while the full count+length+sum bundle is stochastic. V13 isolates whether that instability is caused by conclusion grouping, append/filter sub-lemmas, tree/mirror recursion, or final conjunction reassembly.

Lean remains the only correctness oracle. These fixtures intentionally do **not** bundle `expected_proof.lean`; local witness proofs were used only to validate theorem truth and initial `rfl` failure.

## Fixtures

| Fixture | Purpose |
| --- | --- |
| `challenge_v13_partition_side_bundle_no_stats_flatten_mirror` | Full keep/drop triple metric bundles grouped by side, without unrelated `statsAcc` definitions. |
| `challenge_v13_partition_reordered_metrics_flatten_mirror` | Same full simultaneous metric content as v12, but metric groups are ordered sum/count/length. |
| `challenge_v13_raw_count_length_sum_flatten_mirror` | Raw count, length, and sum through tree mirror, without keep/drop partitioning. |
| `challenge_v13_keep_drop_triple_metrics_append` | List-only append composition for keep/drop count, length, and sum metric bundles. |
| `challenge_v13_partition_metrics_with_append_hyps_flatten_mirror` | Full tree-mirror triple bundle with append/filter composition supplied as theorem hypotheses. |
| `challenge_v13_partition_metrics_from_side_hyps` | Final conjunction reassembly from side-grouped keep/drop metric hypotheses only. |

## Local verification

Each fixture has a local-only witness proof under `/tmp/challenge_v13_*.proof.lean` and was checked with `harness/verify_lean_proof.py`. For all six fixtures:

- local witness proof: Lean verified;
- initial proof `rfl`: Lean rejected;
- bundled `expected_proof.lean`: absent.

## Timeout robustness patch

The v12 triple-bundle repeat exposed a wrapper-timeout gap: a slow seeded subprocess could keep running after the extension-level timeout and leave no attribution aggregate. V13 includes a harness robustness patch before long attribution runs:

- `run_attribution_benchmark.py` now runs child commands in their own process group and terminates the full group on timeout;
- per-command attribution budgets scale with `timeout * maxAttempts * 8 + 600s` and have an 1800s single-fixture floor;
- the Pi extension attribution wrapper now budgets for seeded, unseeded, and direct legs instead of timing out near the first slow seeded leg.

## Suggested attribution command

```bash
npm run benchmark:v13
```

Equivalent Pi tool input:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v13_decomposition_order",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

Use the same controlled comparison interpretation as v8-v12: Pi provider only, no pregeneration, synthetic hints disabled, structured alternate retry, and Lean verification as the only success oracle.
