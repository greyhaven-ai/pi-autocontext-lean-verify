# v7 frontier-plus attribution probe

This is a development-run report for the next unpublished fixture set after the v6 frontier probe. The goal was to combine the hardest v6 pattern (nested tree flattening + mirror + partition/filter + simultaneous statistics) with accumulator generalization and mutually recursive traversals until seeded autocontext became unstable.

## Fixture design

Four new no-expected-proof challenge fixtures were added under `harness/fixtures/` and grouped as `challenge_v7_frontier`:

| Fixture | Targeted stressor |
| --- | --- |
| `challenge_v7_partition_stats_acc_mirror` | partitioned tree mirror invariants lifted through a three-field `statsAcc` accumulator for both kept and dropped sublists |
| `challenge_v7_mutual_values_stats_acc_mirror` | mutually recursive even/odd depth value traversals, then mirror preservation lifted through `statsAcc` |
| `challenge_v7_partition_reassemble_stats_acc_mirror` | target partition + reassembly of mirrored tree traversal, then equivalence to original traversal through `statsAcc` |
| `challenge_v7_tree_mapSucc_stats_acc_mirror` | successor-map over mirrored tree flattening with shifted target and length-shifted sum accumulator |

Guardrails:

- no `expected_proof.lean` files are bundled for these fixtures
- initial `rfl` fails for all four fixtures
- witness proofs were sanity-checked locally with Lean but are not added to the package
- benchmark success is Lean verification of the unchanged theorem template with only `{{PROOF}}` supplied

Validation before the probe:

```bash
npm run validate
python3 tests/verify_expected_proofs.py
# manifest_fixtures=75
# expected_proof_fixtures=52
# expected_proofs_verified=52 failed=0
```

## Probe setup

Run root:

`/tmp/pi-v7-frontier-v6seed-20260511T`

Seed playbook:

`harness/playbooks/challenge_v6_frontier_v1.md` (copied from the seeded v6 run)

Settings:

- provider: `pi`
- `--no-pregenerate`
- synthetic hint candidates disabled
- `--structured-alternate-retry`
- `--max-attempts 2`
- `--rounds 2`
- `--timeout 120`
- Lean verifier: `/tmp/autocontext-elan-home/bin/lean`

## Results

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts | Pregenerate/hint calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| seeded autocontext with v6 playbook | 2 / 4 | 7 | 1043.63s | 9 | 0 / 0 |
| unseeded isolated autocontext | 0 / 4 | 8 | 1055.92s | 8 | 0 / 0 |
| direct Pi repair-loop | 0 / 4 | 4 | 482.03s | n/a | n/a |

Fixture-level:

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | --- | --- | --- |
| `challenge_v7_partition_stats_acc_mirror` | ❌ 262.33s | ❌ 264.54s | ❌ 120.44s |
| `challenge_v7_mutual_values_stats_acc_mirror` | ✅ 303.48s | ❌ 261.16s | ❌ 120.43s |
| `challenge_v7_partition_reassemble_stats_acc_mirror` | ❌ 262.47s | ❌ 267.78s | ❌ 120.70s |
| `challenge_v7_tree_mapSucc_stats_acc_mirror` | ✅ 217.15s | ❌ 263.78s | ❌ 120.46s |

## Interpretation

v7 finally finds the frontier where seeded autocontext becomes unstable under the controlled comparison:

- seeded autocontext dropped from v6 `4/4` to v7 `2/4`
- unseeded isolated autocontext solved none of the four v7 fixtures
- direct Pi repair-loop solved none of the four v7 fixtures
- the failures are concentrated in partition/filter + tree mirror + accumulator composition, especially when both kept and dropped sublists or partition reassembly must be related through a three-field accumulator

The strongest successful seeded cases show that the v6 playbook still transfers to some frontier-plus patterns, including mutually recursive traversals and successor-map/tree/stat shifts. The failures indicate the next useful benchmark frontier: proofs requiring a larger local library of partition-specific helper lemmas before accumulator normalization can finish.


## Seeded-failed stability repeat

The two seeded-failed fixtures were repeated three more times with the same seeded setup:

Run root:

`/tmp/pi-v7-seeded-failed-stability-20260511T`

Settings:

- provider: `pi`
- seed playbook: `harness/playbooks/challenge_v6_frontier_v1.md`
- `--no-pregenerate`
- synthetic hint candidates disabled
- `--structured-alternate-retry`
- `--max-attempts 2`
- `--rounds 2`
- `--timeout 120`

Aggregate repeat result:

| Fixture | Repeated seeded result | Mean elapsed |
| --- | ---: | ---: |
| `challenge_v7_partition_stats_acc_mirror` | 0 / 3 | 264.93s |
| `challenge_v7_partition_reassemble_stats_acc_mirror` | 0 / 3 | 262.48s |
| **Total** | **0 / 6** | — |

Run-level totals: `12` Pi calls, `1579.57s` Pi elapsed, `12` Lean verifier attempts, `0` pregenerate/hint calls. All six failures returned no nontrivial repair candidate; final proof remained `rfl`.

This confirms the v7 partition-heavy accumulator fixtures are a stable seeded frontier, not a one-off stochastic failure.

## Next push

Package v6/v7 as the next benchmark-content release (`0.1.9`) now that the seeded-failed v7 partition fixtures remain unstable across repeated controls. After release, run the registry-installed `0.1.9` v7 attribution smoke/full check without explicit `runRoot` to preserve the `0.1.8` robustness guarantee.
