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
