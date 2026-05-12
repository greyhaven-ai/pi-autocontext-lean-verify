# V14 Metric-Order Permutation Fixtures

`challenge_v14_metric_order_permutations` is a source follow-up to the v13 decomposition/order result. V13 narrowed the full simultaneous keep/drop triple-metric frontier to conclusion ordering/grouping sensitivity: side grouping, raw tree metrics, append/filter sub-lemmas, supplied append/filter hypotheses, and final conjunction reassembly all passed seeded, but the reordered metric grouping `sum/count/length` failed. V14 tests all six metric-order permutations for the same full simultaneous keep/drop count/length/sum tree-mirror theorem shape.

Lean remains the only correctness oracle. These fixtures intentionally do **not** bundle `expected_proof.lean`; local witness proofs were used only to validate theorem truth and initial `rfl` failure.

## Fixtures

| Fixture | Metric group order |
| --- | --- |
| `challenge_v14_order_count_length_sum_flatten_mirror` | count, length, sum |
| `challenge_v14_order_count_sum_length_flatten_mirror` | count, sum, length |
| `challenge_v14_order_length_count_sum_flatten_mirror` | length, count, sum |
| `challenge_v14_order_length_sum_count_flatten_mirror` | length, sum, count |
| `challenge_v14_order_sum_count_length_flatten_mirror` | sum, count, length |
| `challenge_v14_order_sum_length_count_flatten_mirror` | sum, length, count |

## Local verification

Each fixture has a local-only witness proof under `/tmp/challenge_v14_*.proof.lean` and was checked with `harness/verify_lean_proof.py`. For all six fixtures:

- local witness proof: Lean verified;
- initial proof `rfl`: Lean rejected;
- bundled `expected_proof.lean`: absent.

## Suggested attribution command

```bash
npm run benchmark:v14
```

Equivalent Pi tool input:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v14_metric_order_permutations",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

Use the same controlled comparison interpretation as v8-v13: Pi provider only, no pregeneration, synthetic hints disabled, structured alternate retry, and Lean verification as the only success oracle.

## Controlled attribution result

Run root:
`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260512T033346_attribution_challenge_v14_metric_order_permutations`

Settings: Pi provider, v6 seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, no explicit `runRoot`.

| Method | Result | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 5 / 6 | 7 | 1121.69s | 17 |
| unseeded isolated autocontext | 0 / 6 | 12 | 11.26s | 12 |
| direct Pi repair-loop | 0 / 6 | 6 | 728.82s | n/a |

| Fixture | Seeded | Unseeded | Direct |
| --- | ---: | ---: | ---: |
| `challenge_v14_order_count_length_sum_flatten_mirror` | proved | failed | failed |
| `challenge_v14_order_count_sum_length_flatten_mirror` | proved | failed | failed |
| `challenge_v14_order_length_count_sum_flatten_mirror` | failed | failed | failed |
| `challenge_v14_order_length_sum_count_flatten_mirror` | proved | failed | failed |
| `challenge_v14_order_sum_count_length_flatten_mirror` | proved | failed | failed |
| `challenge_v14_order_sum_length_count_flatten_mirror` | proved | failed | failed |

Interpretation: v14 shows the order/grouping frontier is stochastic and not a simple fixed `sum`-first failure. Five of six metric-order permutations solved seeded in this run, including canonical count/length/sum and the sum/count/length order that failed in v13. The only seeded miss was length/count/sum. Unseeded and direct solved none. The frontier is now best characterized as non-canonical conjunction-order sensitivity under a small attempt budget, with strong seeded advantage but remaining variance across equivalent metric-order shapes.

## Focused seeded stability repeat

The v14 miss `challenge_v14_order_length_count_sum_flatten_mirror` was repeated three times in seeded-only mode with the same controlled repair settings (`--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, provider `pi`) under:

`/tmp/pi-v14-order-stability-20260512T`

| Repeat | Seeded result | Final attempt | Pi calls | Pi elapsed | Lean attempts |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | proved | 1 | 1 | 213.56s | 3 |
| 2 | failed | — | 2 | 265.13s | 2 |
| 3 | proved | 1 | 1 | 188.49s | 3 |

Focused repeat aggregate: seeded `2/3`. Including the original v14 full-suite miss, this exact fixture is now seeded `2/4`. Together with the v13 `sum/count/length` repeat, the current evidence supports stochastic order sensitivity rather than a deterministic bad ordering.


## Budget and timeout probes

A full-suite v14 `--max-attempts 3`, `--timeout 120` attribution attempt was abandoned as too noisy/expensive: it completed only the seeded prefix before the outer command timed out. The completed prefix proved `3/4`, including the original v14 `length/count/sum` miss at final attempt 1, but then spent excessive wall-clock on `length/sum/count`. Run root:

`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260512T051712_attribution_challenge_v14_metric_order_permutations`

The isolated v14 miss was then repeated three times with `--max-attempts 3` while keeping `--timeout 120` and the same seeded/no-pregenerate/structured-alternate controls:

`/tmp/pi-order-budget3-focused-20260512T160429Z`

| Repeat | Seeded result | Final attempt | Pi calls | Pi elapsed | Lean attempts | Fixture seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | failed | — | 4 | 539.41s | 3 | 539.93s |
| 2 | failed | — | 4 | 542.82s | 3 | 543.34s |
| 3 | failed | — | 4 | 541.27s | 3 | 543.13s |

All six Pi repair calls across these three focused repeats returned no extracted proof; stderr showed `Pi CLI timed out after 120s`. Raising attempt count alone therefore did not stabilize this fixture under the 120s per-call ceiling.

A separate timeout probe kept the original `--max-attempts 2` but raised `--timeout 240` for one seeded repeat:

`/tmp/pi-order-timeout240-focused-20260512T170137Z`

| Probe | Seeded result | Final attempt | Pi calls | Pi elapsed | Lean attempts | Fixture seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| timeout 240, maxAttempts 2 | proved | 1 | 1 | 319.55s | 3 | 320.25s |

Interpretation: the current frontier is not fixed by adding more attempts under the same 120s provider timeout. For these order-sensitive fixtures, a larger per-call Pi timeout can recover proofs with the original two-attempt harness budget, while unseeded/direct remain unsolved in the controlled v14 attribution baseline; later repeats show timeout 240 is helpful but not a complete stability fix.


## Timeout-240 stability repeat

The v14 `length/count/sum` miss was then repeated three more times with the larger per-call timeout, still using the original two-attempt seeded/no-pregenerate/structured-alternate controls:

`/tmp/pi-order-timeout240-stability-20260512T184828Z`

| Repeat | Seeded result | Final attempt | Pi calls | Pi elapsed | Lean attempts | Fixture seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | proved | 1 | 1 | 419.25s | 3 | 420.13s |
| 2 | failed | — | 2 | 513.43s | 2 | 513.79s |
| 3 | proved | 1 | 2 | 525.84s | 3 | 528.17s |

Timeout-240 repeat aggregate: seeded `2/3`; including the earlier registry timeout-240 smoke, this fixture is `3/4` at timeout 240. Timeout 240 can recover proofs and avoids the pure `0/3` timeout-empty behavior seen when only attempt count was raised, but it does **not** fully stabilize this order-sensitive frontier. Because the focused repeats were still stochastic, the planned full v14 seeded-only timeout-240 suite was skipped as likely costly/noisy.
