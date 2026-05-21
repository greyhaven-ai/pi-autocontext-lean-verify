# V20 description-only skeleton ablation

`challenge_v20_description_only_skeleton` reuses the two clean v18 compact-packer theorem templates but changes the seeded playbook context again. V18 used descriptive skeleton guidance plus `plan_...` labels; v19 used bare labels only. V20 removes the labels and keeps only compact natural-language proof-skeleton descriptions.

## Fixture design

No new theorem templates are introduced. The group reuses:

| Fixture | Theorem shape | V20 seed context |
| --- | --- | --- |
| `challenge_v18_pair_top_packers_clean` | v16 generic pair + top-level Prop packers, no `plan_...` identifiers | compact descriptions only |
| `challenge_v18_named_metric_packers_clean` | v16 named length/count/sum pair packers + top-level Prop packer, no `plan_...` identifiers | compact descriptions only |

The description-only seed says to:

- induct on the `NatTree` argument;
- simplify the leaf case by unfolding local definitions;
- split the node case on whether the value equals the target;
- simplify mirror/flatten/keep/drop/list metrics with append/filter helper hypotheses and subtree induction hypotheses;
- normalize natural-number addition with associativity, commutativity, and left-commutativity;
- finish remaining conjunction packaging with the available packers.

It contains no `plan_...` labels. The reused theorem templates also contain no `plan_...` identifiers.

## Local verification baseline

The reused v18 clean fixtures already have local witness proofs `2/2`, initial `rfl` rejection `2/2`, and no bundled expected proofs.

## Controlled attribution

Run root: `/tmp/pi-v20-attribution-20260513T151845Z`

Settings: Pi provider, v20 description-only seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| Seeded autocontext | 2 / 2 | 2 | 283.29s | 6 |
| Unseeded isolated autocontext | 0 / 2 | 4 | 528.66s | 4 |
| Direct Pi repair loop | 0 / 2 | 2 | 240.81s | n/a |

Both clean fixtures solved under seeded context and failed under unseeded/direct in the attribution run.

## Focused stability repeats

Run root: `/tmp/pi-v20-stability-20260513T153652Z`

Seeded repeats over both fixtures:

| Repeat | Result | Pi calls | Pi elapsed | Lean attempts |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 / 2 | 2 | 293.14s | 6 |
| 2 | 2 / 2 | 2 | 236.77s | 6 |
| 3 | 0 / 2 | 4 | 524.89s | 4 |

The third seeded repeat failed both fixtures after 120s Pi timeout-empty repairs. Per fixture, v20 seeded stability is therefore `2/3` repeats, or `3/4` including the original attribution run.

Unseeded isolated repeats remained stochastic:

| Fixture | Repeat results | Repeats proved | Including attribution |
| --- | --- | ---: | ---: |
| `challenge_v18_pair_top_packers_clean` | failed, proved, proved | 2 / 3 | 2 / 4 |
| `challenge_v18_named_metric_packers_clean` | proved, failed, failed | 1 / 3 | 1 / 4 |

## Interpretation

V20 shows that compact natural-language descriptions alone are enough to recover the target Lean proofs in a controlled seeded attribution run, and direct repair remains `0/2`. However, descriptions without `plan_...` labels do **not** reproduce v18's seeded stability (`3/3` for both shapes). They land at `2/3` for each seeded fixture, with the miss caused by timeout-empty repairs rather than Lean accepting a wrong proof.

Compared with v19, bare labels alone were unstable (`2/3` pair+top, `1/3` named metric). V20 improves the named-metric shape but still falls short of v18. The current ablation frontier is therefore: theorem-level `True` hypotheses are not required; bare labels alone are not sufficient; compact descriptive skeleton text is the main stabilizing ingredient, and labels may provide additional anchoring when paired with that text.

## Post-Pi-0.74 final validation

After publishing `autocontext==0.5.1`, `pi-autocontext@0.2.5`, and validating with Pi CLI `0.74.0`, V20 remained the strongest seed shape in the aligned V18/V20/V23 comparison but did not cleanly stabilize at the controlled 120s baseline.

See `docs/V20_PI074_FINAL_VALIDATION_REPORT.md` for the durable final evidence. In brief: clean post-fix V20 reached `28 / 40` fixture successes over 20 repeats at `timeout=120`, with all 12 timeout-only misses recovering at `timeout=240`. The 240s probes are recovery evidence only and do not change the 120s baseline result.
