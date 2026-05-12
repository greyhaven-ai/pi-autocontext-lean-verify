# V10 StatsAcc-Reification Fixtures

`challenge_v10_stats_reification` is a `0.1.10` follow-up to the v9 composition-gradient suite. V9 showed that scalar and paired length/sum partition-through-mirror obligations are learnable with seed context. V10 isolates the remaining suspected frontier: reifying and using the three-field `statsAcc` accumulator as a `(count, length, sum)` tuple.

Lean remains the only correctness oracle. These fixtures intentionally do **not** bundle `expected_proof.lean`; local witness proofs were used only to validate theorem truth and initial `rfl` failure.

## Fixtures

| Fixture | Isolates |
| --- | --- |
| `challenge_v10_stats_acc_reify_list` | Generic `statsAcc` reification into `(countSlow + hits, lengthSlow + total, sumSlow + sum)`. |
| `challenge_v10_stats_acc_extensional_from_metrics` | `statsAcc` equality from equal count/length/sum metrics on arbitrary lists. |
| `challenge_v10_keep_count_flatten_mirror` | Keep-side count metric through tree mirror. |
| `challenge_v10_drop_count_flatten_mirror` | Drop-side count metric through tree mirror. |
| `challenge_v10_keep_stats_acc_from_metric_hyps` | Keep-side `statsAcc` equality assuming already-proved count/length/sum metric equalities. |
| `challenge_v10_drop_stats_acc_from_metric_hyps` | Drop-side `statsAcc` equality assuming already-proved count/length/sum metric equalities. |

## Local sanity checks

Local, unbundled witness proofs compile for all six fixtures, and the initial `rfl` proof fails for all six.

```text
challenge_v10_stats_acc_reify_list: witness ok, initial rfl fails
challenge_v10_stats_acc_extensional_from_metrics: witness ok, initial rfl fails
challenge_v10_keep_count_flatten_mirror: witness ok, initial rfl fails
challenge_v10_drop_count_flatten_mirror: witness ok, initial rfl fails
challenge_v10_keep_stats_acc_from_metric_hyps: witness ok, initial rfl fails
challenge_v10_drop_stats_acc_from_metric_hyps: witness ok, initial rfl fails
```

## First controlled attribution probe

Run root:
`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260511T205054_attribution_challenge_v10_stats_reification`

Settings: Pi provider through the local package, v6 seed playbook, `--no-pregenerate`, synthetic hint candidates disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, and no explicit `runRoot`.

| Method | Result | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 6 / 6 | 6 | 573.82s | 18 |
| unseeded isolated autocontext | 3 / 6 | 9 | 419.11s | 15 |
| direct Pi repair-loop | 1 / 6 | 6 | 631.15s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| `challenge_v10_stats_acc_reify_list` | proved | proved | failed |
| `challenge_v10_stats_acc_extensional_from_metrics` | proved | failed | failed |
| `challenge_v10_keep_count_flatten_mirror` | proved | proved | failed |
| `challenge_v10_drop_count_flatten_mirror` | proved | proved | proved |
| `challenge_v10_keep_stats_acc_from_metric_hyps` | proved | failed | failed |
| `challenge_v10_drop_stats_acc_from_metric_hyps` | proved | failed | failed |

Interpretation: seeded autocontext solves the entire stats-reification layer. Unseeded can solve the core `statsAcc` reification and standalone count metrics, but fails the extensionality and metric-hypothesis application fixtures. Direct only solves the simplest drop-count-zero metric. This narrows the frontier further: the hard step is not tuple normalization alone, but composing that normalization with metric equalities in the keep/drop tree-mirror setting.

## Suggested attribution command

```bash
npm run benchmark:v10
```

Equivalent Pi action:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v10_stats_reification",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```
