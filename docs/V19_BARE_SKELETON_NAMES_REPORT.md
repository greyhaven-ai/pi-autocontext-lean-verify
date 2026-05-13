# V19 bare skeleton-name ablation

`challenge_v19_bare_skeleton_names` reuses the two clean v18 compact-packer theorem templates but changes the seeded playbook context. Instead of the v18 descriptive prompt-only skeleton section, the v19 seed playbook contains only bare skeleton-name bullets plus a minimal safety note that the labels are not Lean hypotheses and should not be emitted.

## Fixture design

No new theorem templates are introduced. The group reuses:

| Fixture | Theorem shape | V19 seed context |
| --- | --- | --- |
| `challenge_v18_pair_top_packers_clean` | v16 generic pair + top-level Prop packers, no `plan_...` identifiers | bare skeleton-name bullets only |
| `challenge_v18_named_metric_packers_clean` | v16 named length/count/sum pair packers + top-level Prop packer, no `plan_...` identifiers | bare skeleton-name bullets only |

The bare labels are:

- `plan_induct_on_tree`
- `plan_leaf_simp_definitions`
- `plan_node_by_cases_value_eq_target`
- `plan_simp_mirror_flatten_keep_drop_append`
- `plan_normalize_nat_add_assoc_comm_left_comm`
- `plan_finish_with_metric_packers`

The reused v18 clean theorem templates contain no `plan_...` identifiers. The manifest fixture count stays `130`; v19 is a prompt/playbook ablation over existing verifier-only fixtures.

## Local verification baseline

The reused v18 clean fixtures already have local witness proofs `2/2`, initial `rfl` rejection `2/2`, and no bundled expected proofs.

## Controlled attribution

Run root:

`/tmp/pi-v19-attribution-20260513T045954Z`

Settings: Pi provider, v19 bare-name seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 2 / 2 | 3 | 500.25s | 5 |
| unseeded isolated autocontext | 2 / 2 | 2 | 357.00s | 6 |
| direct Pi repair-loop | 0 / 2 | 2 | 240.76s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| pair+top clean packers | proved | proved | failed |
| named metric clean packers | proved | proved | failed |

The full attribution run alone overstates the bare-name signal because unseeded isolated autocontext also solved both fixtures.

## Stability repeats

Run root:

`/tmp/pi-v19-stability-20260513T051835Z`

Seeded repeats used the v19 bare-name seed playbook. Unseeded repeats ran each fixture in isolation with no seed playbook, matching the attribution control.

| Run | Seeded result | Pi calls | Pi elapsed | Lean attempts |
| --- | ---: | ---: | ---: | ---: |
| repeat 1 | 1 / 2 | 4 | 574.51s | 4 |
| repeat 2 | 0 / 2 | 4 | 530.42s | 4 |
| repeat 3 | 2 / 2 | 2 | 382.46s | 6 |

Seeded repeat outcomes by fixture:

| Fixture | Original attribution | Repeat 1 | Repeat 2 | Repeat 3 | Repeats only | Including original |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pair+top clean packers | proved | proved | failed | proved | 2 / 3 | 3 / 4 |
| named metric clean packers | proved | failed | failed | proved | 1 / 3 | 2 / 4 |

Unseeded isolated repeat outcomes:

| Fixture | Original attribution | Repeat 1 | Repeat 2 | Repeat 3 | Repeats only | Including original |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pair+top clean packers | proved | failed | failed | failed | 0 / 3 | 1 / 4 |
| named metric clean packers | proved | failed | failed | proved | 1 / 3 | 2 / 4 |

## Interpretation

V19 shows that the bare semantic label names alone are not enough to reproduce v18's stabilization. The seeded full attribution run solved both fixtures, but focused seeded repeats fell to `1/2`, `0/2`, and `2/2`; the named-metric clean fixture was only `1/3` on repeat (`2/4` including original). This is materially weaker than v18's descriptive prompt-only skeleton context, which repeated `3/3` for both shapes (`4/4` including original).

The ablation separates two effects:

- clean compact-packer theorem shapes are sometimes discoverable without any seed playbook (unseeded full attribution `2/2`, but stochastic on repeats);
- detailed prompt-only skeleton **descriptions** stabilize the proof shape better than bare label names alone.

So the current best recipe is not merely to include semantically suggestive names. It is to provide a compact natural-language proof skeleton that names the tree induction, node case split, append/filter simplification, Nat add normalization, and packer finish while keeping those names out of the theorem statement. Direct Pi repair-loop remained `0/2`.
