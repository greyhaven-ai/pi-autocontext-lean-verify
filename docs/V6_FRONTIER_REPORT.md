# v6 frontier attribution probe

This is a development-run report for the next unpublished fixture set after `pi-autocontext-lean-verify@0.1.8`.

## Fixture design

Four new no-expected-proof challenge fixtures were added under `harness/fixtures/` and grouped as `challenge_v6_frontier`:

| Fixture | Targeted stressor |
| --- | --- |
| `challenge_v6_stats_acc_rev` | reverse preservation for a three-field `statsAcc` accumulator carrying count, length, and sum |
| `challenge_v6_tree_partition_mirror` | nested tree flattening, mirror, target partition, count, and length invariants |
| `challenge_v6_mapSucc_rev_count_sum` | successor-map after reverse, with shifted occurrence count and sum/length relation |
| `challenge_v6_mutual_depth_stats_mirror` | mutually recursive even/odd tree-depth statistics preserved by mirror |

Guardrails:

- no `expected_proof.lean` files are bundled for these fixtures
- initial `rfl` fails for all four fixtures
- witness proofs were sanity-checked locally with Lean but are not added to the package
- benchmark success is Lean verification of the unchanged theorem template with only `{{PROOF}}` supplied

Validation before the probe:

```bash
npm run validate
python3 tests/verify_expected_proofs.py
# manifest_fixtures=71
# expected_proof_fixtures=52
# expected_proofs_verified=52 failed=0
```

## Probe setup

Run root:

`/tmp/pi-v6-frontier-v5seed-20260511T`

Seed playbook:

`harness/playbooks/challenge_v5_attribution_v1.md` (copied from the registry-installed `0.1.8` v5 attribution run)

Settings:

- provider: `pi`
- `--no-pregenerate`
- synthetic hint candidates disabled
- `--structured-alternate-retry`
- `--max-attempts 2`
- `--rounds 2`
- `--timeout 120`
- Lean verifier: `/tmp/autocontext-elan-home/bin/lean`, restored to Lean `4.29.1` after the local elan-home default was found missing

The first all-in-one attribution wrapper hit the outer shell timeout after seeded + part of unseeded had completed. Remaining unseeded/direct legs were continued manually with the same settings, then aggregated into `attribution_benchmark_summary.json` and `attribution_benchmark_report.md` under the run root.

## Results

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts | Pregenerate/hint calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| seeded autocontext with v5 playbook | 4 / 4 | 4 | 524.86s | 12 | 0 / 0 |
| unseeded isolated autocontext | 3 / 4 | 5 | 669.44s | 11 | 0 / 0 |
| direct Pi repair-loop | 2 / 4 | 4 | 381.42s | n/a | n/a |

Fixture-level:

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | --- | --- | --- |
| `challenge_v6_stats_acc_rev` | ✅ 131.36s | ✅ 175.81s | ✅ 67.40s |
| `challenge_v6_tree_partition_mirror` | ✅ 180.34s | ❌ 261.33s | ❌ 120.37s |
| `challenge_v6_mapSucc_rev_count_sum` | ✅ 129.38s | ✅ 153.15s | ❌ 120.36s |
| `challenge_v6_mutual_depth_stats_mirror` | ✅ 86.05s | ✅ 81.20s | ✅ 73.29s |

## Interpretation

This is the current strongest frontier probe:

- seeded autocontext solved all four new no-gold fixtures
- unseeded isolated autocontext failed the nested tree/partition/mirror fixture
- direct Pi failed the nested tree/partition/mirror fixture and the map/reverse/sum/count fixture
- even at v6, the mutually recursive even/odd-depth fixture was not a frontier for either unseeded or direct prompting

The useful frontier appears to be **nested composition of tree flattening + mirror + partition/filter + simultaneous count/length invariants**, not mutual recursion by itself. A next v6b/v7 push should combine that nested composition with accumulator generalization and/or mutually recursive tree/list traversals.
