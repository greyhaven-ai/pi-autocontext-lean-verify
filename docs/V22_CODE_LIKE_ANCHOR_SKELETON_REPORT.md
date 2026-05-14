# V22 Code-Like Anchor Skeleton Ablation

## Question

V18 was stable when compact proof-skeleton descriptions were paired with code-like `plan_...` labels in seeded prompt context. V19 showed bare labels alone are insufficient. V20 showed descriptions alone are capable but not fully stable. V21 showed neutral prose anchors plus descriptions are worse than description-only context.

V22 asks whether the stabilizing part of V18 is the code-like anchor style rather than the exact `plan_` prefix: keep the compact descriptions, add snake_case code-like anchors, and deliberately omit the earlier detailed-plan prefix.

## Setup

- Fixture group: `challenge_v22_code_like_anchor_skeleton`
- Reused theorem templates:
  - `challenge_v18_pair_top_packers_clean`
  - `challenge_v18_named_metric_packers_clean`
- Seed playbook: `harness/playbooks/challenge_v22_code_like_anchor_skeleton_v1.md`
- Seed anchors:
  - `tree_induction_step`
  - `leaf_simplification_step`
  - `node_value_target_split_step`
  - `append_filter_simplification_step`
  - `nat_add_normalization_step`
  - `metric_packer_finish_step`
- Confirmed seed playbook contains no `plan_` token.
- Candidate still supplies only `{{PROOF}}`.
- Lean verification remains the only success oracle.
- Controlled baseline: `--no-pregenerate`, no synthetic hints, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

## Attribution run

Root: `/tmp/pi-v22-attribution-20260514T025938Z`

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| Seeded autocontext | 2 / 2 | 2 | 288.05s | 6 |
| Unseeded isolated autocontext | 0 / 2 | 4 | 520.42s | 4 |
| Direct Pi repair-loop | 0 / 2 | 2 | 240.83s | n/a |

Fixture split:

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| `challenge_v18_pair_top_packers_clean` | proved | failed | failed |
| `challenge_v18_named_metric_packers_clean` | proved | failed | failed |

## Seeded stability repeats

Root: `/tmp/pi-v22-stability-20260514T031802Z`

| Repeat | Proved | Pair+top | Named metric | Pi calls | Pi elapsed | Lean attempts |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 / 2 | failed | proved | 3 | 388.52s | 5 |
| 2 | 1 / 2 | proved | failed | 3 | 416.26s | 5 |
| 3 | 2 / 2 | proved | proved | 3 | 519.69s | 5 |

Seeded repeat totals:

- Pair+top: `2 / 3` repeats, or `3 / 4` including the attribution run.
- Named metric: `2 / 3` repeats, or `3 / 4` including the attribution run.
- Aggregate seeded repeats: `4 / 6`, or `6 / 8` including attribution.

## Interpretation

V22 is capable: seeded context solved both fixtures in the controlled attribution run while unseeded and direct solved none. However, V22 did **not** reproduce V18's seeded `3/3` per-fixture stability. Its seeded repeat profile (`2/3` per fixture, `3/4` including attribution) is closer to V20 description-only context than to V18 prompt-only descriptions plus `plan_...` labels.

This suggests that merely making anchors code-like and snake_case is not sufficient to explain V18 stabilization. The exact V18 label form, the `plan_` prefix, or the interaction between detailed labels and descriptions may be contributing additional anchoring. V22 therefore narrows the prompt-transfer hypothesis: code-like anchors without the earlier detailed-plan prefix recover attribution success but not full stability.
