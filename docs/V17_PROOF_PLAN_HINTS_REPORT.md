# V17 proof-plan skeleton hint diagnostics

`challenge_v17_proof_plan_hints` is a post-`0.1.12` diagnostic suite that keeps the hard v16 compact-packer theorem shapes and adds harmless proof-plan/skeleton hint hypotheses. Each hint has type `True`: it carries no mathematical content and cannot prove the target, but its name exposes the intended proof plan to the repair prompt.

## Fixture design

All four fixtures intentionally ship without `expected_proof.lean`; local witness proofs are used only to prove theorem truth and are not bundled.

| Fixture | Packer shape | Proof-plan hint shape | Intent |
| --- | --- | --- | --- |
| `challenge_v17_pair_top_packers_with_coarse_plan_hints` | generic pair + top-level Prop packers | `use_tree_induction`, `split_node_on_target`, `simp_with_append_filter_helpers`, `finish_with_metric_packers` | Test compact coarse skeleton names on a v16 stochastic miss. |
| `challenge_v17_pair_top_packers_with_detailed_plan_hints` | generic pair + top-level Prop packers | induction, leaf simp, node case split, simp helper set, Nat add normalization, packer finish | Test whether more detailed names help or add prompt noise. |
| `challenge_v17_named_metric_packers_with_coarse_plan_hints` | named length/count/sum pair packers + top-level Prop packer | same coarse skeleton names | Test compact coarse names with metric-local packers. |
| `challenge_v17_named_metric_packers_with_detailed_plan_hints` | named length/count/sum pair packers + top-level Prop packer | same detailed skeleton names | Test detailed names with metric-local packers. |

## Local verification

| Check | Result |
| --- | ---: |
| Local witness proofs | 4 / 4 |
| Initial `rfl` rejected | 4 / 4 |
| Bundled expected proofs | 0 |

## Controlled attribution

Run root:

`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260513T010738Z_attribution_benchmark_challenge_v17_proof_plan_hints`

Settings: Pi provider, v6 seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 4 / 4 | 4 | 375.19s | 12 |
| unseeded isolated autocontext | 0 / 4 | 8 | 7.22s | 8 |
| direct Pi repair-loop | 1 / 4 | 4 | 459.00s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| pair+top packers, coarse plan hints | proved | failed | failed |
| pair+top packers, detailed plan hints | proved | failed | proved |
| named metric packers, coarse plan hints | proved | failed | failed |
| named metric packers, detailed plan hints | proved | failed | failed |

All seeded repairs used the target proof shape (`induction`, `simp`, `Nat.add_assoc`, `Nat.add_comm`, `Nat.add_left_comm`) at final attempt 1. The detailed plan-hint proofs also explicitly referenced the harmless `True` plan names with `have _ := ...`, confirming the names were visible to and usable by the model without contributing mathematical content.

## Seeded stability repeats

The v17 group was repeated three more times in seeded-only mode with the same baseline settings to avoid overinterpreting a single full-suite success.

Run root:

`/tmp/pi-v17-seeded-stability-20260513T012244Z`

| Run | Result | Pi calls | Pi elapsed | Lean attempts |
| --- | ---: | ---: | ---: | ---: |
| repeat 1 | 3 / 4 | 8 | 1169.41s | 9 |
| repeat 2 | 3 / 4 | 5 | 528.40s | 11 |
| repeat 3 | 4 / 4 | 4 | 529.30s | 12 |

Per-fixture repeat outcomes:

| Fixture | Original attribution | Repeat 1 | Repeat 2 | Repeat 3 | Repeats only | Including original |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pair+top, coarse plan hints | proved | failed | proved | proved | 2 / 3 | 3 / 4 |
| pair+top, detailed plan hints | proved | proved | proved | proved | 3 / 3 | 4 / 4 |
| named metric, coarse plan hints | proved | proved | failed | proved | 2 / 3 | 3 / 4 |
| named metric, detailed plan hints | proved | proved | proved | proved | 3 / 3 | 4 / 4 |

## Interpretation

V17 gives the cleanest prompt-shape signal so far:

- seeded autocontext solved the full v17 suite on the first controlled attribution run (`4/4`) while unseeded remained `0/4`;
- direct Pi solved only the pair+top detailed-plan fixture (`1/4`), so the hints help direct search somewhat but do not erase the seeded advantage;
- detailed proof-plan names were stable across repeats (`3/3`, `4/4` including original for both packer shapes);
- coarse proof-plan names improved over v16 but remained stochastic (`2/3`, `3/4` including original).

This separates the frontier more sharply: the missing ingredient is not more mathematical hypotheses or longer timeout. Compact, harmless proof-plan names that spell out the induction/case-split/simp/add-normalization skeleton materially improve seeded repair stability. However, coarse names still leave stochastic failures, so the robust recipe appears to be **detailed skeleton naming**, not merely adding any extra `True` context.
