# Proof-Transfer Benchmark

This package includes no-expected-proof challenge fixtures for reproducible Lean proof-transfer probes. They are deliberately separate from the original expected-proof corpus: Lean verification remains the oracle, but the package does not bundle gold proof bodies for these challenge fixtures.

## Challenge groups

| Group | Fixtures | Purpose |
| --- | ---: | --- |
| `challenge_v2_no_helper` | 3 | List proofs requiring local append/map helper lemma discovery. |
| `challenge_v3_generalization` | 4 | Theorem-generalization proofs requiring accumulator generalization and multi-helper proof plans. |
| `challenge_transfer` | 7 | All v2/v3 challenge fixtures. |
| `challenge_v4_count` | 4 | Count/list/tree fixtures covering occurrence counts, reverse, tree mirror/flatten, and successor-map-after-reverse. |
| `challenge_v5_attribution` | 4 | Simultaneous invariants and multi-helper composition fixtures designed to compare seeded, unseeded, and direct repair. |
| `challenge_v5_tree_tally` | 1 | The hard v5 tree/tally mirror fixture for attribution repeats. |
| `challenge_v6_frontier` | 4 | Frontier fixtures covering multi-accumulator reverse invariants, nested tree partition stats, successor-map reverse count/sum, and mutual tree stats. |
| `challenge_v7_frontier` | 4 | Frontier-plus fixtures combining partition/tree mirror composition with stats accumulator normalization. |
| `challenge_v8_diagnostics` | 4 | Diagnostic fixtures isolating the v7 partition-heavy accumulator frontier into smaller components. |
| `challenge_v9_composition_gradient` | 6 | Composition-gradient fixtures splitting keep/drop partition-through-mirror into scalar and paired length/sum obligations. |
| `challenge_v10_stats_reification` | 6 | StatsAcc-reification fixtures isolating tuple normalization, metric extensionality, count metrics, and stats equality from metric hypotheses. |
| `challenge_v11_metric_composition` | 6 | Metric-composition fixtures combining keep/drop metric bundles with statsAcc extensionality boundaries. |
| `challenge_v12_simultaneous_metrics` | 7 | Simultaneous-metric fixtures splitting keep/drop count-only, length-only, sum-only, pair, and triple metric bundles. |
| `challenge_v13_decomposition_order` | 6 | Decomposition/order fixtures isolating triple-bundle grouping, append/filter sub-lemmas, raw tree metrics, and conjunction reassembly. |
| `challenge_v14_metric_order_permutations` | 6 | Metric-order permutation fixtures covering all six count/length/sum orderings in the full simultaneous keep/drop triple bundle. |
| `challenge_v15_proof_shape_hints` | 4 | Proof-shape hint fixtures exposing metric-bundle, side-bundle, append/filter, and reassembly hypotheses for the hard length/count/sum order. |
| `challenge_v16_compact_reassembly_hints` | 4 | Compact reassembly-hint fixtures replacing the large v15 higher-order hypothesis with generic/named packers. |
| `challenge_v17_proof_plan_hints` | 4 | Proof-plan skeleton hint fixtures adding harmless `True` induction/case-split/simp/add-normalization names. |
| `challenge_v18_prompt_only_skeleton_hints` | 2 | Prompt-only skeleton hint fixtures reusing v16 theorem statements while putting detailed proof-plan names only in the seeded playbook. |
| `challenge_v19_bare_skeleton_names` | 2 | Bare-name ablation reusing the clean v18 fixtures with only skeleton-label bullets in the seeded playbook. |
| `challenge_extended_transfer` | 78 | All v2/v3/v4/v5/v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16/v17/v18 challenge fixtures. |

## Reproducible commands

Seeded autocontext vs direct Pi repair-loop:

```bash
npm run benchmark:v3
npm run benchmark:v4
npm run benchmark:v5
npm run benchmark:v6
npm run benchmark:v7
npm run benchmark:v8
npm run benchmark:v9
npm run benchmark:v10
npm run benchmark:v11
npm run benchmark:v12
npm run benchmark:v13
npm run benchmark:v14
npm run benchmark:v15
npm run benchmark:v16
npm run benchmark:v17
npm run benchmark:v18
npm run benchmark:v19
```

Seeded autocontext vs unseeded isolated autocontext vs direct Pi repair-loop:

```bash
npm run benchmark:v5:attribution
npm run benchmark:v6
npm run benchmark:v7
npm run benchmark:v8
npm run benchmark:v9
npm run benchmark:v10
npm run benchmark:v11
npm run benchmark:v12
npm run benchmark:v13
npm run benchmark:v14
npm run benchmark:v15
npm run benchmark:v16
npm run benchmark:v17
npm run benchmark:v18
npm run benchmark:v19
```

Equivalent explicit harness invocations:

```bash
python3 harness/run_proof_transfer_benchmark.py \
  --fixture-group challenge_v5_attribution \
  --timeout 120 \
  --max-attempts 2 \
  --rounds 2

python3 harness/run_attribution_benchmark.py \
  --fixture-group challenge_v5_attribution \
  --timeout 120 \
  --max-attempts 2 \
  --rounds 2
```

The benchmark runners preserve the guardrails:

- provider: `pi`
- autocontext runtime: `uvx --python 3.12 --from autocontext==0.4.8 autoctx improve`
- `--no-pregenerate`
- `--structured-alternate-retry`
- synthetic hint candidates disabled
- Lean verification is the only success oracle

Outputs are written under a short temp directory by default, `the system temp directory (`pi-autocontext-lean-verify/...`)/...`, to avoid long Pi session paths when the package is loaded from npm temp `node_modules`. Set `AUTOCONTEXT_LEAN_VERIFY_RESULTS_ROOT` or pass `--run-root` / tool `runRoot` to override.

Artifacts include:

- `proof_transfer_benchmark_summary.json` / `proof_transfer_benchmark_report.md`
- `attribution_benchmark_summary.json` / `attribution_benchmark_report.md`
- method-specific stdout/stderr/command logs

## Local evidence snapshot

### v3 theorem-generalization repeated stability

| Method | Trials | Proofs | Success rate | Pi calls |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 3 | 12 / 12 | 100.0% | 12 |
| direct Pi repair-loop | 3 | 7 / 12 | 58.3% | 12 |

Hard-plus subset (`challenge_v3_tree_flatten_mirror`, `challenge_v3_map_rev_append_combined`): seeded autocontext `6 / 6`, direct Pi repair-loop `1 / 6`.

### v4 count/list/tree stability

| Method | Trials | Proofs | Success rate | Pi calls |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 3 × 4 | 12 / 12 | 100.0% | 12 |
| direct Pi repair-loop | 3 × 4 | 3 / 12 | 25.0% | 12 |
| unseeded isolated autocontext | 1 × 4 | 4 / 4 | 100.0% | 5 |

Interpretation: v4 shows the verifier-backed autocontext harness is robust compared with direct repair-loop, but it does not prove seed context is necessary because unseeded isolated solved all four.

### v5 attribution

| Method | Full v5 set | Hard tree/tally repeats |
| --- | ---: | ---: |
| seeded autocontext, v4 playbook | 4 / 4 | 3 / 3 |
| unseeded isolated autocontext | 3 / 4 | 1 / 3 |
| direct Pi repair-loop | 1 / 4 | 0 / 3 |

Interpretation: v5 is the strongest proof-transfer signal so far. The verifier-backed autocontext harness beats direct repair-loop overall, and seeded playbook context improves stability on the multi-helper tree/tally composition fixture.

## Guardrails

- Candidate supplies only `{{PROOF}}`.
- The theorem template is fixed.
- No `sorry`, `admit`, new axioms, `unsafe`, new imports, or theorem weakening.
- Lean verification is required before any success is counted.
- Challenge fixtures intentionally omit `expected_proof.lean`.


## v6/v7 frontier suites

Version `0.1.9` adds two frontier attribution groups:

- `challenge_v6_frontier`: seeded `4/4`, unseeded `3/4`, direct `2/4` in the development probe.
- `challenge_v7_frontier`: seeded `2/4`, unseeded `0/4`, direct `0/4`; the two seeded-failed partition-heavy fixtures repeated at `0/6`.

Run from a checkout with:

```bash
npm run benchmark:v6
npm run benchmark:v7
npm run benchmark:v8
npm run benchmark:v9
npm run benchmark:v10
npm run benchmark:v11
npm run benchmark:v12
npm run benchmark:v13
npm run benchmark:v14
```

Or through Pi with `action="attribution"` and the corresponding `fixtureGroup`.


## v8 diagnostic suite

Version `0.1.10` adds `challenge_v8_diagnostics`, a four-fixture suite that decomposes the v7 partition-heavy accumulator frontier into smaller theorem obligations:

- raw `statsAcc` invariance through tree mirror, before partitioning;
- keep-side partition stats through tree mirror;
- drop-side partition stats through tree mirror;
- list-only partition/reassembly equivalence for `statsAcc`.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first two controlled attribution probes solved seeded `6/8`, unseeded `1/8`, and direct `0/8`: raw tree/mirror stats and list-only reassembly are stable for seeded autocontext, while keep/drop partition-through-mirror remains stochastic. This indicates the v7 instability is mainly compositional.


## v9 composition-gradient suite

Version `0.1.10` adds `challenge_v9_composition_gradient`, a six-fixture suite focused on the stochastic keep/drop partition-through-mirror components:

- keep-side length through tree mirror;
- keep-side sum through tree mirror;
- paired keep-side length+sum through tree mirror;
- drop-side length through tree mirror;
- drop-side sum through tree mirror;
- paired drop-side length+sum through tree mirror.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `6/6`, unseeded `1/6`, and direct `0/6`, indicating length/sum partition-through-mirror obligations are learnable with seed context and the remaining frontier is likely `statsAcc` triple reification/composition.


## v10 stats-reification suite

Version `0.1.10` adds `challenge_v10_stats_reification`, a six-fixture suite focused on the `statsAcc` triple reification frontier:

- generic reification of `statsAcc` into `(count, length, sum)` metrics;
- extensionality of `statsAcc` from equal count/length/sum metrics;
- keep-side and drop-side count metrics through tree mirror;
- keep-side and drop-side `statsAcc` equality from already-proved metric equalities.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `6/6`, unseeded `3/6`, and direct `1/6`: unseeded can solve core reification/count metrics, but seed context is needed for extensionality and metric-hypothesis application.


## v11 metric-composition suite

Version `0.1.10` adds `challenge_v11_metric_composition`, a six-fixture suite bridging metric proofs and `statsAcc` equality without asking the model to synthesize the full v7/v8 theorem outright:

- keep-side and drop-side metric bundles through tree mirror;
- keep-side and drop-side `statsAcc` equality from bundled metric proofs;
- combined keep/drop metric bundles;
- combined keep/drop stats equality from metric bundles.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `5/6`, unseeded `0/6`, and direct `1/6`, with the only seeded miss on the combined keep/drop metric-bundle proof.


## v12 simultaneous-metric suite

Version `0.1.10` adds `challenge_v12_simultaneous_metrics`, a seven-fixture suite isolating the combined keep/drop metric-bundle proof:

- simultaneous keep/drop count metrics;
- simultaneous keep/drop length metrics;
- simultaneous keep/drop sum metrics;
- simultaneous count+length, count+sum, and length+sum metric pairs;
- simultaneous count+length+sum metric bundle.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `6/7`, unseeded `0/7`, and direct `0/7`: all one-metric and two-metric simultaneous bundles solved seeded, while the full count+length+sum bundle failed. Isolated repeats of that triple bundle show seeded stochasticity (`1/3` across full-suite plus isolated observations), not theorem falsehood.


## v13 decomposition/order suite

Version `0.1.11` adds `challenge_v13_decomposition_order`, a six-fixture suite isolating the v12 full-triple metric frontier:

- full keep/drop triple metric bundles grouped by side and stripped of unrelated `statsAcc` definitions;
- full simultaneous metric content with a different metric-group order;
- raw count/length/sum metrics through tree mirror without keep/drop;
- list-only append composition for keep/drop count/length/sum;
- full tree-mirror triple bundle with append/filter composition supplied as hypotheses;
- conjunction reassembly from side-grouped keep/drop metric hypotheses.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `5/6`, unseeded `0/6`, and direct `1/6`. Raw tree metrics, list-only append composition, supplied append/filter hypotheses, side-grouped bundles, and final conjunction reassembly all solved seeded. The only seeded miss was the reordered full simultaneous metric grouping, pointing to proof-search sensitivity to conjunction ordering/grouping rather than theorem falsehood or missing low-level lemmas.


## v14 metric-order permutation suite

Version `0.1.11` also adds `challenge_v14_metric_order_permutations`, a six-fixture suite testing every metric-order permutation of the full simultaneous keep/drop count/length/sum tree-mirror theorem:

- count, length, sum;
- count, sum, length;
- length, count, sum;
- length, sum, count;
- sum, count, length;
- sum, length, count.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `5/6`, unseeded `0/6`, and direct `0/6`. Canonical count/length/sum and the v13-failed sum/count/length order both solved seeded; the only seeded miss was length/count/sum. Focused seeded-only repeats then solved the v13 `sum/count/length` miss `2/3` and the v14 `length/count/sum` miss `2/3`, indicating stochastic/non-canonical conjunction-order sensitivity rather than a simple fixed `sum`-first failure. A budget follow-up showed that adding attempts alone (`maxAttempts=3`, timeout 120s) produced only Pi-timeout-empty repairs on the two misses. Increasing the per-call timeout to 240s with the original `maxAttempts=2` can recover proofs, but focused stability repeats were still `2/3` for each miss (`3/4` each including the earlier timeout-240 smoke), so timeout 240 is a useful robustness knob rather than a full stabilization fix.


## v15 proof-shape hint suite

Version `0.1.12` adds `challenge_v15_proof_shape_hints`, a four-fixture diagnostic suite for the hard length/count/sum full simultaneous keep/drop theorem shape:

- metric-grouped hypotheses only;
- side-grouped keep/drop hypotheses only;
- append metric plus keep/drop append helper hypotheses;
- append/filter helper hypotheses plus an explicit final reassembly hypothesis.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. The first controlled attribution probe solved seeded `3/4`, unseeded `0/4`, and direct `2/4`. Direct solved the two pure reassembly fixtures, proving final conjunction assembly is not the frontier by itself. Seeded also solved the append/filter-hypothesis tree-induction fixture while direct and unseeded failed it, showing the v6 seed playbook still contributes proof-shape transfer. The only seeded miss was the append/filter-plus-explicit-reassembly-hyp fixture, suggesting the explicit reassembly hypothesis added prompt/type complexity rather than removing the bottleneck. Focused seeded repeats strengthened that split: append/filter hypotheses repeated `3/3` (`4/4` including the original attribution), while append/filter plus explicit reassembly repeated only `1/3` (`1/4` including original).


## v16 compact reassembly hint suite

Version `0.1.13` adds `challenge_v16_compact_reassembly_hints`, a four-fixture diagnostic suite that keeps the hard v15 length/count/sum simultaneous keep/drop theorem shape but replaces the large tree-specific higher-order reassembly hypothesis with compact packer hypotheses:

- top-level generic Prop packer;
- generic Prop pair packer plus top-level packer;
- generic first-order Nat scalar equality packer;
- named length/count/sum pair packers plus top-level packer.

These fixtures intentionally ship without `expected_proof.lean`; local witness proofs were used only to verify theorem truth and are not bundled. Local witnesses verify `4/4`, and initial `rfl` is rejected for `4/4`. The first controlled attribution probe solved seeded `2/4`, unseeded `0/4`, and direct `0/4`. Seeded solved the top-level Prop packer and generic Nat scalar packer variants, while the pair+top and named-metric variants missed in the full-suite run. Focused seeded repeats of those two misses then solved each `2/3` (`2/4` each including the original miss), showing they are stochastic rather than impossible. A timeout-240 focused probe improved named-metric repeats to `3/3`, but pair+top remained `2/3` and the run showed severe wall-clock blowups after Pi timeout messages. V16 therefore supports the v15 prompt-shape diagnosis: compact reassembly hints are less harmful than a large tree-specific higher-order hypothesis, but the remaining bottleneck is still stochastic recognition of the tree-induction/simp proof shape under a small repair budget; timeout 240 is recoverability evidence, not a clean stabilization strategy.


## v17 proof-plan skeleton hint suite

Version `0.1.13` also adds `challenge_v17_proof_plan_hints`, a four-fixture suite that keeps the hard v16 compact packer shapes and adds harmless proof-plan/skeleton hint hypotheses of type `True`. The hints carry no mathematical content; their names expose the intended proof plan: tree induction, leaf simplification, node case split on `value = target`, simplification with append/filter helpers, Nat addition normalization, and packer-based finish.

Local witnesses verify `4/4`, and initial `rfl` is rejected for `4/4`. The first controlled attribution probe solved seeded `4/4`, unseeded `0/4`, and direct `1/4` at the baseline timeout 120. Seeded proofs all used the target induction/simp/add-normalization shape at final attempt 1. A seeded-only stability repeat showed a split by hint granularity: detailed plan hints repeated `3/3` for both pair+top and named-metric packer shapes (`4/4` including the original attribution), while coarse plan hints repeated `2/3` for each (`3/4` including original). V17 therefore indicates that the missing prompt structure is not more mathematical content or a longer timeout; detailed proof skeleton names materially improve seeded stability while preserving Lean as the only success oracle.


## V18 prompt-only skeleton hints

The source tree after `0.1.13` adds `challenge_v18_prompt_only_skeleton_hints`, a two-fixture diagnostic suite that keeps the v16 compact-packer theorem statements but removes the v17 harmless `True` plan hypotheses. Detailed skeleton names are supplied only by `harness/playbooks/challenge_v18_prompt_only_skeleton_v1.md` during seeded attribution.

Local witnesses verify `2/2`, initial `rfl` is rejected for `2/2`, and no expected proofs are bundled. The controlled Pi attribution run at timeout 120 solved seeded `2/2`, unseeded `1/2`, and direct `0/2`. Focused stability repeats showed seeded prompt-only skeleton context is stable (`3/3` repeats for both pair+top and named-metric clean fixtures, `4/4` including original), while unseeded remains stochastic (`1/3` repeats for each fixture; `1/4` pair+top and `2/4` named-metric including original). V18 therefore strengthens the v17 interpretation: detailed skeleton names need not be theorem hypotheses, but in prompt-only form they stabilize rather than exclusively enable proof search.


## V19 bare skeleton-name ablation

The source tree after v18 adds `challenge_v19_bare_skeleton_names`, an ablation group that reuses the two clean v18 theorem templates but swaps the seeded context from descriptive prompt-only skeleton guidance to bare semantic labels only. The manifest fixture count stays `130`; the group points at `challenge_v18_pair_top_packers_clean` and `challenge_v18_named_metric_packers_clean`.

The controlled Pi attribution run solved seeded `2/2`, unseeded `2/2`, and direct `0/2`. Focused repeats then showed bare names do **not** preserve the v18 stabilization: seeded repeats were pair+top `2/3` and named metric `1/3` (`3/4` and `2/4` including original), while unseeded repeats were pair+top `0/3` and named metric `1/3` (`1/4` and `2/4` including original). V19 therefore points to the descriptive proof skeleton text, not just semantic labels, as the stabilizing prompt ingredient.
