# V18 prompt-only skeleton hint diagnostics

`challenge_v18_prompt_only_skeleton_hints` tests whether the v17 detailed proof-plan signal survives when the skeleton names are removed from theorem hypotheses and supplied only through seeded prompt/playbook context.

The two fixture templates intentionally reuse the hard v16 compact-packer theorem statements. They do **not** contain the v17 `True` proof-plan hypotheses or any `plan_...` identifiers. The seeded attribution path uses `harness/playbooks/challenge_v18_prompt_only_skeleton_v1.md`, which appends detailed skeleton-name guidance to the v6 frontier seed playbook. Unseeded isolated autocontext and direct Pi repair-loop do not receive that seed playbook context.

## Fixture design

All fixtures intentionally ship without `expected_proof.lean`; local witness proofs are used only to prove theorem truth and are not bundled.

| Fixture | Theorem shape | Prompt-only skeleton context | Intent |
| --- | --- | --- | --- |
| `challenge_v18_pair_top_packers_clean` | v16 generic pair + top-level Prop packers | detailed plan names in seed playbook only | Test whether the v17 pair+top detailed-plan stabilization persists without theorem-level `True` hints. |
| `challenge_v18_named_metric_packers_clean` | v16 named length/count/sum pair packers + top-level Prop packer | detailed plan names in seed playbook only | Test whether the v17 named-metric detailed-plan stabilization persists without theorem-level `True` hints. |

The prompt-only skeleton names are:

- `plan_induct_on_tree`
- `plan_leaf_simp_definitions`
- `plan_node_by_cases_value_eq_target`
- `plan_simp_mirror_flatten_keep_drop_append`
- `plan_normalize_nat_add_assoc_comm_left_comm`
- `plan_finish_with_metric_packers`

They are not in Lean scope for v18; candidates that reference them should fail Lean. The neutral v18 fixture ids and theorem names avoid embedding those skeleton names in the fixed theorem template.

## Local verification

| Check | Result |
| --- | ---: |
| Local witness proofs | 2 / 2 |
| Initial `rfl` rejected | 2 / 2 |
| Bundled expected proofs | 0 |

## Controlled attribution

Run root:

`/tmp/pi-v18-neutral-attribution-20260513T035352Z`

Settings: Pi provider, v18 prompt-only seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 2 / 2 | 2 | 252.88s | 6 |
| unseeded isolated autocontext | 1 / 2 | 4 | 565.49s | 4 |
| direct Pi repair-loop | 0 / 2 | 2 | 240.75s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| pair+top clean packers | proved | failed | failed |
| named metric clean packers | proved | proved | failed |

Both seeded proofs used the intended induction/simp/add-normalization shape and did not reference any `plan_...` names.

## Stability repeats

Run root:

`/tmp/pi-v18-neutral-stability-20260513T041201Z`

Seeded repeats used the same v18 prompt-only seed playbook. Unseeded repeats ran each fixture in isolation with no seed playbook, matching the attribution control.

| Run | Seeded result | Pi calls | Pi elapsed | Lean attempts |
| --- | ---: | ---: | ---: | ---: |
| repeat 1 | 2 / 2 | 3 | 446.80s | 5 |
| repeat 2 | 2 / 2 | 2 | 207.26s | 6 |
| repeat 3 | 2 / 2 | 2 | 275.73s | 6 |

Unseeded isolated repeats:

| Fixture | Original attribution | Repeat 1 | Repeat 2 | Repeat 3 | Repeats only | Including original |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pair+top clean packers | failed | failed | proved | failed | 1 / 3 | 1 / 4 |
| named metric clean packers | proved | proved | failed | failed | 1 / 3 | 2 / 4 |

Seeded prompt-only repeats by fixture:

| Fixture | Original attribution | Repeat 1 | Repeat 2 | Repeat 3 | Repeats only | Including original |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pair+top clean packers | proved | proved | proved | proved | 3 / 3 | 4 / 4 |
| named metric clean packers | proved | proved | proved | proved | 3 / 3 | 4 / 4 |

## Interpretation

V18 preserves the main v17 signal without theorem-level `True` hypotheses: detailed skeleton names in the seeded playbook were enough for seeded autocontext to solve both clean v16 theorem shapes in the attribution run and all three focused repeats (`4/4` observations per fixture including the original run).

However, V18 also shows that the clean compact-packer theorem shapes are occasionally discoverable without a seed playbook. Unseeded isolated autocontext solved one fixture in the full attribution run and one repeat for each fixture. This means prompt-only skeleton context is a **stabilizer**, not an exclusive source of capability: it turns a stochastic unseeded proof search into stable seeded recognition of the induction/by-cases/simp/add-normalization skeleton. Direct Pi repair-loop remained `0/2`.

Compared with v16, which used the same theorem shapes under the standard v6 seed and repeated only `2/3` for each focused compact-packer miss, the v18 prompt-only skeleton seed reaches `3/3` for both shapes, matching v17 detailed theorem-level hints while keeping the theorem statements clean.
