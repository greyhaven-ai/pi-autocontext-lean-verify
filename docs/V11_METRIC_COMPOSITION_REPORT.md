# V11 Metric-Composition Fixtures

`challenge_v11_metric_composition` is a source-only follow-up to the v10 stats-reification suite. V10 showed that seed context solves tuple reification and metric-hypothesis application, while unseeded struggles with extensionality. V11 bridges the v9 metric layer and v10 extensionality layer without asking for the full v7/v8 stats-accumulator theorem outright.

Lean remains the only correctness oracle. These fixtures intentionally do **not** bundle `expected_proof.lean`; local witness proofs were used only to validate theorem truth and initial `rfl` failure.

## Fixtures

| Fixture | Isolates |
| --- | --- |
| `challenge_v11_keep_metric_bundle_flatten_mirror` | Keep-side count/length/sum metric bundle through tree mirror. |
| `challenge_v11_drop_metric_bundle_flatten_mirror` | Drop-side count/length/sum metric bundle through tree mirror. |
| `challenge_v11_keep_stats_acc_from_metric_bundle` | Keep-side `statsAcc` equality from a bundled metric proof. |
| `challenge_v11_drop_stats_acc_from_metric_bundle` | Drop-side `statsAcc` equality from a bundled metric proof. |
| `challenge_v11_partition_metric_bundles_flatten_mirror` | Combined keep/drop metric bundles through tree mirror, without statsAcc equality. |
| `challenge_v11_partition_stats_from_metric_bundles` | Combined keep/drop `statsAcc` equality from bundled metric proofs. |

## Local sanity checks

Local, unbundled witness proofs compile for all six fixtures, and the initial `rfl` proof fails for all six.

```text
challenge_v11_keep_metric_bundle_flatten_mirror: witness ok, initial rfl fails
challenge_v11_drop_metric_bundle_flatten_mirror: witness ok, initial rfl fails
challenge_v11_keep_stats_acc_from_metric_bundle: witness ok, initial rfl fails
challenge_v11_drop_stats_acc_from_metric_bundle: witness ok, initial rfl fails
challenge_v11_partition_metric_bundles_flatten_mirror: witness ok, initial rfl fails
challenge_v11_partition_stats_from_metric_bundles: witness ok, initial rfl fails
```

## First controlled attribution probe

Run root:
`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260511T212529_attribution_challenge_v11_metric_composition`

Settings: Pi provider through the local package, v6 seed playbook, `--no-pregenerate`, synthetic hint candidates disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, and no explicit `runRoot`.

| Method | Result | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 5 / 6 | 7 | 948.47s | 17 |
| unseeded isolated autocontext | 0 / 6 | 12 | 14.59s | 12 |
| direct Pi repair-loop | 1 / 6 | 6 | 690.64s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| `challenge_v11_keep_metric_bundle_flatten_mirror` | proved | failed | failed |
| `challenge_v11_drop_metric_bundle_flatten_mirror` | proved | failed | failed |
| `challenge_v11_keep_stats_acc_from_metric_bundle` | proved | failed | failed |
| `challenge_v11_drop_stats_acc_from_metric_bundle` | proved | failed | failed |
| `challenge_v11_partition_metric_bundles_flatten_mirror` | failed | failed | failed |
| `challenge_v11_partition_stats_from_metric_bundles` | proved | failed | proved |

Interpretation: seeded solves one-sided metric bundles and one-sided metric-bundle-to-`statsAcc` applications, but fails the combined keep/drop metric-bundle theorem in this probe. The surprising direct success on the final hypothesis-driven partition stats theorem confirms that applying already-provided metric bundles can be simple when the metric proof obligation is absent. The hard bridge is now specifically the combined keep/drop metric-bundle proof, which is close to the full v7/v8 composition pressure but still excludes `statsAcc` equality.

## Suggested attribution command

```bash
npm run benchmark:v11
```

Equivalent Pi action:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v11_metric_composition",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```
