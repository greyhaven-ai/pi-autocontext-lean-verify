# V12 Simultaneous-Metric Fixtures

`challenge_v12_simultaneous_metrics` is a `0.1.10` follow-up to the v11 metric-composition suite. V11 showed that one-sided keep/drop metric bundles were solvable with seed context, but the combined keep/drop metric bundle was the remaining miss. V12 splits that combined bundle by metric type and by incremental pair/triple composition.

Lean remains the only correctness oracle. These fixtures intentionally do **not** bundle `expected_proof.lean`; local witness proofs were used only to validate theorem truth and initial `rfl` failure.

## Fixtures

| Fixture | Isolates |
| --- | --- |
| `challenge_v12_partition_count_metrics_flatten_mirror` | Simultaneous keep/drop count metrics through tree mirror. |
| `challenge_v12_partition_length_metrics_flatten_mirror` | Simultaneous keep/drop length metrics through tree mirror. |
| `challenge_v12_partition_sum_metrics_flatten_mirror` | Simultaneous keep/drop sum metrics through tree mirror. |
| `challenge_v12_partition_count_length_metrics_flatten_mirror` | Simultaneous keep/drop count+length metric pairs. |
| `challenge_v12_partition_count_sum_metrics_flatten_mirror` | Simultaneous keep/drop count+sum metric pairs. |
| `challenge_v12_partition_length_sum_metrics_flatten_mirror` | Simultaneous keep/drop length+sum metric pairs. |
| `challenge_v12_partition_count_length_sum_metrics_flatten_mirror` | Simultaneous keep/drop count+length+sum metric bundle. |

## Local sanity checks

Local, unbundled witness proofs compile for all seven fixtures, and the initial `rfl` proof fails for all seven.

```text
challenge_v12_partition_count_metrics_flatten_mirror: witness ok, initial rfl fails
challenge_v12_partition_length_metrics_flatten_mirror: witness ok, initial rfl fails
challenge_v12_partition_sum_metrics_flatten_mirror: witness ok, initial rfl fails
challenge_v12_partition_count_length_metrics_flatten_mirror: witness ok, initial rfl fails
challenge_v12_partition_count_sum_metrics_flatten_mirror: witness ok, initial rfl fails
challenge_v12_partition_length_sum_metrics_flatten_mirror: witness ok, initial rfl fails
challenge_v12_partition_count_length_sum_metrics_flatten_mirror: witness ok, initial rfl fails
```

## First controlled attribution probe

Run root:
`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260511T215957_attribution_challenge_v12_simultaneous_metrics`

Settings: Pi provider through the local package, v6 seed playbook, `--no-pregenerate`, synthetic hint candidates disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, and no explicit `runRoot`.

| Method | Result | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 6 / 7 | 8 | 1044.92s | 20 |
| unseeded isolated autocontext | 0 / 7 | 14 | 12.71s | 14 |
| direct Pi repair-loop | 0 / 7 | 7 | 843.04s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| `challenge_v12_partition_count_metrics_flatten_mirror` | proved | failed | failed |
| `challenge_v12_partition_length_metrics_flatten_mirror` | proved | failed | failed |
| `challenge_v12_partition_sum_metrics_flatten_mirror` | proved | failed | failed |
| `challenge_v12_partition_count_length_metrics_flatten_mirror` | proved | failed | failed |
| `challenge_v12_partition_count_sum_metrics_flatten_mirror` | proved | failed | failed |
| `challenge_v12_partition_length_sum_metrics_flatten_mirror` | proved | failed | failed |
| `challenge_v12_partition_count_length_sum_metrics_flatten_mirror` | failed | failed | failed |

Interpretation: seeded solves every simultaneous keep/drop single-metric and two-metric pair, but missed the full simultaneous count+length+sum metric bundle in the full-suite run. Follow-up isolated repeats show that triple bundle is stochastic rather than impossible: seeded solved it once and failed it twice across the full-suite plus isolated observations. Unseeded and direct have not solved it.

## Full triple-bundle stability repeats

After the first full v12 probe, the failing triple-bundle fixture was repeated in isolation with the same controlled settings and no explicit `runRoot`:

| Run | Run root | Seeded | Unseeded | Direct | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| Full v12 suite | `20260511T215957_attribution_challenge_v12_simultaneous_metrics` | failed | failed | failed | Full seven-fixture run; triple bundle was the only seeded miss. |
| Isolated repeat 1 | `20260511T223947_attribution_challenge_v12_simultaneous_metrics` | proved | failed | failed | Seeded `1` Pi call, `212.00s`, `3` Lean attempts. |
| Isolated repeat 2 | `20260511T224607_attribution_challenge_v12_simultaneous_metrics` | failed | not run | not run | Seeded artifact completed after wrapper timeout; `2` Pi calls, `1648.45s`, `3` Lean attempts; no attribution summary was generated. |

Seeded aggregate for the triple bundle across these observations is `1/3`; unseeded/direct remain `0/2` where those legs completed. This changes the diagnosis from stable failure to stochastic frontier: the full count+length+sum simultaneous bundle is solvable by seeded autocontext, but not reliably under the controlled two-attempt budget.

## Suggested attribution command

```bash
npm run benchmark:v12
```

Equivalent Pi action:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v12_simultaneous_metrics",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```
