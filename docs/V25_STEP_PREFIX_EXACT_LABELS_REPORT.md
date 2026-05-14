# V25 Step-Prefix Exact-Label Ablation

## Question

V23 showed that V18's exact semantic label roots without the original prefix do not reproduce V18 stability. V24 showed that the original prefix with shorter generic labels also does not reproduce V18 stability. V25 tests a third possibility: keep the exact semantic roots from V18, but attach a different code-like prefix.

This asks whether any prefixed exact semantic label is enough, or whether V18's original prefixed form is special.

## Setup

- Fixture group: `challenge_v25_step_prefix_exact_labels`
- Reused theorem templates:
  - `challenge_v18_pair_top_packers_clean`
  - `challenge_v18_named_metric_packers_clean`
- Seed playbook: `harness/playbooks/challenge_v25_step_prefix_exact_labels_v1.md`
- Step-prefixed exact label roots:
  - `step_induct_on_tree`
  - `step_leaf_simp_definitions`
  - `step_node_by_cases_value_eq_target`
  - `step_simp_mirror_flatten_keep_drop_append`
  - `step_normalize_nat_add_assoc_comm_left_comm`
  - `step_finish_with_metric_packers`
- Candidate still supplies only `{{PROOF}}`.
- Lean verification remains the only success oracle.
- Controlled baseline: `--no-pregenerate`, no synthetic hints, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

## Focused seeded probes

Root: `/tmp/pi-v25-focused-seeded-20260514T170102Z`

The v25 plan was intentionally defensive: run focused seeded repeats first, and only proceed to expensive attribution components if the `step_` exact-root labels showed V18-like stability. The watchdog did not fire in any focused seeded repeat.

| Repeat | Proved | Pair+top | Named metric | Pi calls | Pi elapsed | Lean attempts | External watchdog |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 / 2 | proved | failed | 3 | 348.76s | 5 | no |
| 2 | 0 / 2 | failed | failed | 4 | 524.36s | 4 | no |
| 3 | 2 / 2 | proved | proved | 2 | 186.76s | 6 | no |

Focused seeded totals:

- Pair+top: `2 / 3`.
- Named metric: `1 / 3`.
- Aggregate: `3 / 6`.

## Attribution components

Not run. Because focused seeded probes were not stable and included a clean `0/2` miss, the expensive unseeded/direct attribution components were skipped under the defensive v25 plan.

## Interpretation

V25 does not reproduce V18 stability. The step-prefixed exact label roots can solve both fixtures in one repeat, but they are less stable than V18 and weaker than the v22/v23/v24 partial-stability profile on the named-metric fixture in this small sample.

Combined with V23 and V24, the prompt-transfer hypothesis is now sharper:

- V23: exact roots without the original prefix are capable but not stable.
- V24: original prefix with generic labels is capable but not stable.
- V25: alternate prefix with exact roots is capable but not stable.
- V18 remains the strongest stability signal: the original prefix plus exact semantically rich label wording paired with compact descriptions.

The literal original prefixed label form appears to matter more than either the exact roots alone or the existence of a generic code-like prefix.

## Runtime note

No outer watchdog fired for the v25 focused seeded repeats, and no new active `uvx/autoctx` process group remained after the run. The second timeout hardening patch therefore did not show a new orphan/pipe-leak failure in this focused probe, although failed repeats still consumed several hundred seconds of Pi elapsed time.
