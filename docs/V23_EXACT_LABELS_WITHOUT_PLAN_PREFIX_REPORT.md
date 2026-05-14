# V23 Exact Labels Without Detailed-Plan Prefix Ablation

## Question

V18 was stable when compact proof-skeleton descriptions were paired with exact code-like labels using a detailed-plan prefix. V22 showed that changing both the prefix and the wording to new snake_case step anchors recovered attribution success but not V18-level stability.

V23 isolates the prefix: keep V18's detailed label wording and descriptions, but remove only the detailed-plan prefix.

## Setup

- Fixture group: `challenge_v23_exact_labels_without_plan_prefix`
- Reused theorem templates:
  - `challenge_v18_pair_top_packers_clean`
  - `challenge_v18_named_metric_packers_clean`
- Seed playbook: `harness/playbooks/challenge_v23_exact_labels_without_plan_prefix_v1.md`
- Seed labels:
  - `induct_on_tree`
  - `leaf_simp_definitions`
  - `node_by_cases_value_eq_target`
  - `simp_mirror_flatten_keep_drop_append`
  - `normalize_nat_add_assoc_comm_left_comm`
  - `finish_with_metric_packers`
- Confirmed the seed playbook contains no `plan_` token.
- Candidate still supplies only `{{PROOF}}`.
- Lean verification remains the only success oracle.
- Controlled baseline: `--no-pregenerate`, no synthetic hints, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

## Initial attribution attempt

Root: `/tmp/pi-v23-attribution-20260514T043941Z`

The full attribution harness was curtailed by the outer 7200s command limit before it could write `attribution_benchmark_summary.json`. The available component summaries are still useful but are treated as partial evidence.

| Component | Proved | Pi calls | Pi elapsed | Lean attempts | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Seeded autocontext | 1 / 2 | 4 | 539.03s | 4 | pair+top proved; named metric failed |
| Unseeded pair+top | 1 / 1 | 1 | 152.56s | 3 | proved |
| Unseeded named metric | 0 / 1 | 2 | 4337.81s | 2 | failed with severe runtime pathology |
| Direct pair+top | 0 / 1 | 1 | n/a | n/a | `DIRECT_PI_TIMEOUT`; elapsed 2383.76s in summary |
| Direct named metric | not run | n/a | n/a | n/a | curtailed before this fixture |

This run shows v23 is not immediately stable: seeded missed the named-metric shape in the first full attribution attempt. It also preserves the timeout/runtime caveat: some Pi calls still greatly exceeded nominal 120s timeout accounting even though process cleanup avoided persistent active autocontext jobs after manual cleanup.

## Focused seeded retry set

Root: `/tmp/pi-v23-retry-seeded-20260514T145916Z`

These retries used the same controlled proof settings and an outer watchdog only to avoid orphaned process groups. The watchdog did not fire in any counted retry.

| Retry | Proved | Pair+top | Named metric | Pi calls | Pi elapsed | Lean attempts | External watchdog |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 / 2 | proved | proved | 2 | 261.77s | 6 | no |
| 2 | 0 / 2 | failed | failed | 4 | 526.83s | 4 | no |
| 3 | 2 / 2 | proved | proved | 2 | 239.66s | 6 | no |

Focused seeded retry totals:

- Pair+top: `2 / 3` retries.
- Named metric: `2 / 3` retries.
- Aggregate: `4 / 6` seeded retry fixtures.

Including the initial partial attribution seeded attempt:

- Pair+top: `3 / 4`.
- Named metric: `2 / 4`.
- Aggregate: `5 / 8`.

## Interpretation

V23 does not reproduce V18 stability. Removing only the detailed-plan prefix from V18's exact labels makes the behavior worse than V18 and at least as stochastic as V20/V22. The focused retry set shows v23 can solve both fixtures in a given run, but it also produced a clean `0/2` seeded miss under the same baseline settings.

This supports the hypothesis that the full V18 label form contributes meaningful prompt anchoring. The prefix itself, or the model's learned association with labels shaped like detailed proof-plan identifiers, appears to matter beyond generic snake_case anchors and beyond descriptions alone.

## Timeout/process note

The v23 probes also show that runtime pathology is reduced but not eliminated as an experimental concern. A first focused seeded attempt at `/tmp/pi-v23-focused-seeded-20260514T093551Z` was curtailed after an outer timeout left an `uvx/autoctx` process group active; that group was manually terminated and is not counted as proof evidence. The successful retry set used an independent watchdog and completed without watchdog intervention.
