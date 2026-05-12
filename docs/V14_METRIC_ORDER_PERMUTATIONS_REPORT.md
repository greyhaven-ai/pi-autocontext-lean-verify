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
