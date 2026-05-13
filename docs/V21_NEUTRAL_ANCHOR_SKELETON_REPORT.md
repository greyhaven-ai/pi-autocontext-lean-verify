# V21 neutral-anchor skeleton ablation

`challenge_v21_neutral_anchor_skeleton` reuses the two clean v18 compact-packer theorem templates but changes the seeded playbook context one more time. V18 used descriptive skeleton guidance plus code-like `plan_...` labels; v19 used bare labels only; v20 used compact descriptions without labels. V21 keeps compact descriptions and adds neutral natural-language step anchors without using `plan_...` tokens in the seed playbook.

## Fixture design

No new theorem templates are introduced. The group reuses:

| Fixture | Theorem shape | V21 seed context |
| --- | --- | --- |
| `challenge_v18_pair_top_packers_clean` | v16 generic pair + top-level Prop packers, no `plan_...` identifiers | neutral anchors + compact descriptions |
| `challenge_v18_named_metric_packers_clean` | v16 named length/count/sum pair packers + top-level Prop packer, no `plan_...` identifiers | neutral anchors + compact descriptions |

The neutral-anchor seed says to use these prompt-only steps:

- Tree induction;
- Leaf simplification;
- Node equality split;
- Append/filter simplification;
- Nat addition normalization;
- Packer finish.

Each anchor is paired with a compact natural-language description of the intended proof step. The seed playbook contains no `plan_...` tokens, and the reused theorem templates also contain no `plan_...` identifiers.

## Local verification baseline

The reused v18 clean fixtures already have local witness proofs `2/2`, initial `rfl` rejection `2/2`, and no bundled expected proofs.

## Controlled attribution

Run root: `/tmp/pi-v21-attribution-20260513T174308Z`

Settings: Pi provider, v21 neutral-anchor seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| Seeded autocontext | 1 / 2 | 3 | 417.34s | 5 |
| Unseeded isolated autocontext | 1 / 2 | 3 | 361.52s | 5 |
| Direct Pi repair loop | 0 / 2 | 2 | 240.83s | n/a |

Fixture-level split:

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | --- | --- | --- |
| `challenge_v18_pair_top_packers_clean` | failed | proved | failed |
| `challenge_v18_named_metric_packers_clean` | proved | failed | failed |

## Focused stability probes

Run root: `/tmp/pi-v21-stability-20260513T180052Z`

The first seeded repeat over both fixtures failed both fixtures and exposed a severe wall-clock blowup:

| Probe | Result | Pi calls | Pi elapsed | Lean attempts | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Seeded repeat 1 | 0 / 2 | 4 | 4704.63s | 4 | pair+top timeout-empty; named-metric returned no candidate after a `fetch failed` repair path and pathological wall time |
| Seeded repeat 2 | incomplete | 2 | 901.02s before interruption | 2 | pair+top failed; named-metric alternate repair was killed after the outer command timeout left orphaned processes |

A small follow-up unseeded probe at `/tmp/pi-v21-focused-20260513T200809Z` proved pair+top `1/1`, but with another pathological wall time (`1412.05s` Pi elapsed). The unseeded named-metric follow-up was killed before producing a summary. These follow-ups are retained as timeout/wall-clock pathology evidence rather than clean stability counts.

## Interpretation

V21 does **not** close the v20-to-v18 stability gap. Neutral anchors plus descriptions solved only `1/2` seeded in the controlled attribution run, while unseeded also solved `1/2` and direct remained `0/2`. The first seeded stability repeat then dropped to `0/2`, and further probing became dominated by severe wall-clock blowups and timeout-empty/no-candidate repairs.

Compared with earlier ablations:

- v18 descriptions plus `plan_...` labels: seeded stable `3/3` per fixture;
- v19 bare labels: unstable (`2/3` pair+top, `1/3` named metric);
- v20 descriptions only: capable but not fully stable (`2/3` per seeded fixture);
- v21 neutral anchors plus descriptions: worse than v20 in the first attribution/stability probes and introduces more pathological wall-clock behavior.

The current evidence suggests the v18 stabilization was not merely generic sectioning/anchor structure. Code-like skeleton labels paired with compact descriptions may provide a more useful retrieval/anchoring signal than neutral prose headings, but this remains a stochastic frontier and all positive claims are Lean-verifier-backed only.
