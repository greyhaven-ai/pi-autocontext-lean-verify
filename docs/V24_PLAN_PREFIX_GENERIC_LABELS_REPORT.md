# V24 Generic Plan-Prefix Label Ablation

## Question

V23 showed that keeping V18's exact detailed label wording but removing the `plan_` prefix did not reproduce V18 stability. V24 tests the complementary direction: keep the `plan_` prefix, but replace V18's exact detailed labels with shorter generic labels.

This asks whether the prefix itself is a major stabilizing anchor, or whether V18 needs the full exact label form.

## Setup

- Fixture group: `challenge_v24_plan_prefix_generic_labels`
- Reused theorem templates:
  - `challenge_v18_pair_top_packers_clean`
  - `challenge_v18_named_metric_packers_clean`
- Seed playbook: `harness/playbooks/challenge_v24_plan_prefix_generic_labels_v1.md`
- Generic seed labels:
  - `plan_tree_induction`
  - `plan_leaf_simplification`
  - `plan_node_split`
  - `plan_append_filter_simplification`
  - `plan_nat_add_normalization`
  - `plan_packer_finish`
- Confirmed the seed playbook includes these generic `plan_` labels and excludes V18's exact detailed labels:
  - `plan_induct_on_tree`
  - `plan_leaf_simp_definitions`
  - `plan_node_by_cases_value_eq_target`
  - `plan_simp_mirror_flatten_keep_drop_append`
  - `plan_normalize_nat_add_assoc_comm_left_comm`
  - `plan_finish_with_metric_packers`
- Candidate still supplies only `{{PROOF}}`.
- Lean verification remains the only success oracle.
- Controlled baseline: `--no-pregenerate`, no synthetic hints, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

## Focused seeded probes

Root: `/tmp/pi-v24-focused-seeded-20260514T160030Z`

The v24 plan was intentionally defensive: run focused seeded repeats first, and only proceed to expensive attribution components if the generic prefix labels showed promising stability. The watchdog did not fire in any focused seeded repeat.

| Repeat | Proved | Pair+top | Named metric | Pi calls | Pi elapsed | Lean attempts | External watchdog |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 / 2 | failed | proved | 4 | 561.45s | 4 | no |
| 2 | 1 / 2 | proved | failed | 3 | 373.54s | 5 | no |
| 3 | 2 / 2 | proved | proved | 2 | 272.80s | 6 | no |

Focused seeded totals:

- Pair+top: `2 / 3`.
- Named metric: `2 / 3`.
- Aggregate: `4 / 6`.

## Attribution components

Not run. Because focused seeded probes were only `2/3` per fixture and showed the same cross-over instability seen in v22/v23, the expensive unseeded/direct attribution components were skipped under the defensive v24 plan.

## Interpretation

V24 does not reproduce V18 stability. Generic `plan_` labels can solve both fixtures in one repeat, but the prefix alone is insufficient: the first two repeats each miss one fixture, and the per-fixture stability is `2/3`, matching the v20/v22/v23 partial-stability profile rather than V18's seeded `3/3` per fixture.

Combined with V23, this narrows the prompt-transfer hypothesis:

- Removing only the prefix from V18 exact labels breaks stability.
- Keeping the prefix but changing to generic labels also fails to restore stability.
- Therefore V18's stabilization likely depends on the full detailed label form: the `plan_` prefix plus exact, semantically rich label wording paired with compact descriptions.

## Runtime note

No outer watchdog fired for the v24 focused seeded repeats, and no new active `uvx/autoctx` process group remained after the run. However, wall-clock/Pi elapsed is still high for failed repeats, so timeout/runtime pathology remains an experimental caveat for future attribution components.
