# V8 Diagnostic Frontier Fixtures

`challenge_v8_diagnostics` is a source-only follow-up suite after the `0.1.9` v6/v7 frontier release. It isolates the hardest v7 pattern — partition/filter plus tree mirror plus three-field accumulator normalization — into smaller theorem obligations.

Lean remains the only correctness oracle. These fixtures intentionally do **not** bundle `expected_proof.lean`; local witness proofs were used only to validate that each theorem is true and that the initial `rfl` proof fails.

## Fixtures

| Fixture | Isolates |
| --- | --- |
| `challenge_v8_stats_acc_flatten_mirror` | Raw `statsAcc` invariance through `flatten (mirror tree)`, before keep/drop partitioning. |
| `challenge_v8_keep_stats_acc_flatten_mirror` | Keep-side partition stats through tree mirror, separated from the drop-side conjunct. |
| `challenge_v8_drop_stats_acc_flatten_mirror` | Drop-side partition stats through tree mirror, separated from the keep-side conjunct. |
| `challenge_v8_partition_reassemble_stats_acc_list` | List-only `keep ++ drop` partition reassembly through `statsAcc`, without tree mirror. |

## Local sanity checks

Local, unbundled witness proofs compile for all four fixtures:

```text
challenge_v8_stats_acc_flatten_mirror: witness ok, initial rfl fails
challenge_v8_keep_stats_acc_flatten_mirror: witness ok, initial rfl fails
challenge_v8_drop_stats_acc_flatten_mirror: witness ok, initial rfl fails
challenge_v8_partition_reassemble_stats_acc_list: witness ok, initial rfl fails
```

The purpose of v8 is diagnostic rather than release evidence: determine whether the v7 instability comes from raw tree/mirror accumulator invariance, keep/drop partition invariance individually, list-only partition reassembly, or only from composing those ingredients in the full v7 theorem.

## First controlled attribution probe

Run root:
`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260511T183609_attribution_challenge_v8_diagnostics`

Settings: Pi provider through the local package, `--no-pregenerate`, synthetic hint candidates disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`, and no explicit `runRoot`.

| Method | Result | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 4 / 4 | 6 | 898.34s | 10 |
| unseeded isolated autocontext | 1 / 4 | 7 | 450.79s | 9 |
| direct Pi repair-loop | 0 / 4 | 4 | 481.67s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| `challenge_v8_stats_acc_flatten_mirror` | proved | failed | failed |
| `challenge_v8_keep_stats_acc_flatten_mirror` | proved | failed | failed |
| `challenge_v8_drop_stats_acc_flatten_mirror` | proved | proved | failed |
| `challenge_v8_partition_reassemble_stats_acc_list` | proved | failed | failed |

Interpretation: decomposing v7 into smaller obligations restores seeded stability (`4/4`) while unseeded only solves the drop-side mirror component and direct solves none. The v7 failure therefore appears to come from composing individually learnable ingredients, especially keep-side partition stats and list-only reassembly, rather than from theorem falsehood or raw tree/mirror accumulator invariance alone.

## Suggested attribution command

```bash
npm run benchmark:v8
```

Equivalent Pi action:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v8_diagnostics",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```
