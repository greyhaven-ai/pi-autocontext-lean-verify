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

## Controlled attribution result

Run root:
`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260512T024818_attribution_challenge_v13_decomposition_order`

Settings: Pi provider, v6 seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, no explicit `runRoot`.

| Method | Result | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 5 / 6 | 8 | 1039.35s | 16 |
| unseeded isolated autocontext | 0 / 6 | 12 | 10.82s | 12 |
| direct Pi repair-loop | 1 / 6 | 6 | 621.65s | n/a |

| Fixture | Seeded | Unseeded | Direct |
| --- | ---: | ---: | ---: |
| `challenge_v13_partition_side_bundle_no_stats_flatten_mirror` | proved | failed | failed |
| `challenge_v13_partition_reordered_metrics_flatten_mirror` | failed | failed | failed |
| `challenge_v13_raw_count_length_sum_flatten_mirror` | proved | failed | failed |
| `challenge_v13_keep_drop_triple_metrics_append` | proved | failed | failed |
| `challenge_v13_partition_metrics_with_append_hyps_flatten_mirror` | proved | failed | failed |
| `challenge_v13_partition_metrics_from_side_hyps` | proved | failed | proved |

Interpretation: the v12/v13 frontier is not raw tree-mirror metrics, not append/filter sub-lemma synthesis, not final conjunction reassembly, and not side-grouped keep/drop triple bundles once unrelated `statsAcc` definitions are removed. The remaining miss is the reordered all-three simultaneous metric grouping (`sum`, then `count`, then `length`), where seeded stayed at `0/1` and unseeded/direct also failed. This points to proof-search sensitivity to conjunction ordering/grouping in the full simultaneous metric bundle, rather than theorem falsehood or missing low-level lemmas.

## Focused seeded stability repeat

The v13 miss `challenge_v13_partition_reordered_metrics_flatten_mirror` was repeated three times in seeded-only mode with the same controlled repair settings (`--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, provider `pi`) under:

`/tmp/pi-v14-order-stability-20260512T`

| Repeat | Seeded result | Final attempt | Pi calls | Pi elapsed | Lean attempts |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | failed | — | 2 | 265.13s | 2 |
| 2 | proved | 1 | 1 | 132.60s | 3 |
| 3 | proved | 1 | 1 | 105.07s | 3 |

Focused repeat aggregate: seeded `2/3`. Including the original v13 full-suite miss, this exact fixture is now seeded `2/4`; including the equivalent v14 `sum/count/length` success, the theorem-shape/order observation is `3/5`. This confirms the v13 miss was stochastic, not a stable failure of the `sum/count/length` ordering.


## Budget and timeout probes

A focused attempt-budget probe repeated the same v13 miss three times with `--max-attempts 3` while keeping `--timeout 120` and the same seeded/no-pregenerate/structured-alternate controls:

`/tmp/pi-order-budget3-focused-20260512T160429Z`

| Repeat | Seeded result | Final attempt | Pi calls | Pi elapsed | Lean attempts | Fixture seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | failed | — | 4 | 545.17s | 3 | 550.59s |
| 2 | failed | — | 4 | 552.76s | 3 | 554.74s |
| 3 | failed | — | 4 | 543.11s | 3 | 544.98s |

All six Pi repair calls across these three repeats returned no extracted proof; stderr showed `Pi CLI timed out after 120s`. Raising attempt count alone therefore did not stabilize this fixture under the 120s per-call ceiling.

A separate timeout probe kept the original `--max-attempts 2` but raised `--timeout 240` for one seeded repeat:

`/tmp/pi-order-timeout240-focused-20260512T170137Z`

| Probe | Seeded result | Final attempt | Pi calls | Pi elapsed | Lean attempts | Fixture seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| timeout 240, maxAttempts 2 | proved | 1 | 1 | 336.86s | 3 | 337.59s |

Interpretation: for the v13 reordered full-bundle miss, provider wall-clock timeout is a more useful knob than additional repair attempts at the same 120s timeout, but later repeats show it is not a complete stability fix.


## Timeout-240 stability repeat

The v13 reordered miss was then repeated three more times with the larger per-call timeout, still using the original two-attempt seeded/no-pregenerate/structured-alternate controls:

`/tmp/pi-order-timeout240-stability-20260512T184828Z`

| Repeat | Seeded result | Final attempt | Pi calls | Pi elapsed | Lean attempts | Fixture seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | failed | — | 2 | 512.75s | 2 | 514.77s |
| 2 | proved | 1 | 1 | 251.80s | 3 | 254.20s |
| 3 | proved | 1 | 1 | 266.91s | 3 | 267.75s |

Timeout-240 repeat aggregate: seeded `2/3`; including the earlier timeout-240 smoke, this fixture is `3/4` at timeout 240. Timeout 240 can recover proofs and avoids the pure `0/3` timeout-empty behavior seen when only attempt count was raised, but it does **not** fully stabilize this order-sensitive frontier.
