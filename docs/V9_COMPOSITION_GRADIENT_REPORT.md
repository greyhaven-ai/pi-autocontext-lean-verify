# V9 Composition-Gradient Fixtures

`challenge_v9_composition_gradient` is a source-only follow-up to the v8 diagnostic suite. V8 showed that raw tree/mirror `statsAcc` and list-only partition reassembly were stable for seeded autocontext, while keep/drop partition-through-mirror components were stochastic. V9 splits those partition-through-mirror components into scalar length/sum obligations and paired length+sum obligations.

Lean remains the only correctness oracle. These fixtures intentionally do **not** bundle `expected_proof.lean`; local witness proofs were used only to validate theorem truth and initial `rfl` failure.

## Fixtures

| Fixture | Isolates |
| --- | --- |
| `challenge_v9_keep_length_flatten_mirror` | Keep-side filtered length through tree mirror. |
| `challenge_v9_keep_sum_flatten_mirror` | Keep-side filtered sum through tree mirror. |
| `challenge_v9_keep_length_sum_flatten_mirror` | Paired keep-side length+sum through tree mirror. |
| `challenge_v9_drop_length_flatten_mirror` | Drop-side filtered length through tree mirror. |
| `challenge_v9_drop_sum_flatten_mirror` | Drop-side filtered sum through tree mirror. |
| `challenge_v9_drop_length_sum_flatten_mirror` | Paired drop-side length+sum through tree mirror. |

## Local sanity checks

Local, unbundled witness proofs compile for all six fixtures, and the initial `rfl` proof fails for all six.

```text
challenge_v9_keep_length_flatten_mirror: witness ok, initial rfl fails
challenge_v9_keep_sum_flatten_mirror: witness ok, initial rfl fails
challenge_v9_keep_length_sum_flatten_mirror: witness ok, initial rfl fails
challenge_v9_drop_length_flatten_mirror: witness ok, initial rfl fails
challenge_v9_drop_sum_flatten_mirror: witness ok, initial rfl fails
challenge_v9_drop_length_sum_flatten_mirror: witness ok, initial rfl fails
```

## First controlled attribution probe

Run root:
`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260511T200540_attribution_challenge_v9_composition_gradient`

Settings: Pi provider through the local package, v6 seed playbook, `--no-pregenerate`, synthetic hint candidates disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, and no explicit `runRoot`.

| Method | Result | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 6 / 6 | 6 | 680.86s | 18 |
| unseeded isolated autocontext | 1 / 6 | 11 | 241.20s | 14 |
| direct Pi repair-loop | 0 / 6 | 6 | 722.36s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| `challenge_v9_keep_length_flatten_mirror` | proved | failed | failed |
| `challenge_v9_keep_sum_flatten_mirror` | proved | failed | failed |
| `challenge_v9_keep_length_sum_flatten_mirror` | proved | failed | failed |
| `challenge_v9_drop_length_flatten_mirror` | proved | failed | failed |
| `challenge_v9_drop_sum_flatten_mirror` | proved | proved | failed |
| `challenge_v9_drop_length_sum_flatten_mirror` | proved | failed | failed |

Interpretation: all scalar and paired length/sum partition-through-mirror obligations are stable in the first seeded probe. Since v8 keep/drop `statsAcc` fixtures remained stochastic while these scalar/pair obligations solve cleanly, the remaining frontier appears to be `statsAcc` triple reification/composition over filtered mirrored traversals, not the length/sum invariants themselves.

## Suggested attribution command

```bash
npm run benchmark:v9
```

Equivalent Pi action:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v9_composition_gradient",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```
