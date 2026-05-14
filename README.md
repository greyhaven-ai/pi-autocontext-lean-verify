# pi-autocontext-lean-verify

Experimental Pi package for verifier-backed Lean proof repair using autocontext and Pi.

Working product framing:

> A Pi plugin for verifier-backed formal proof repair using autocontext and Lean.

This is **not** a general theorem prover and should not be described as “autocontext proves theorems.” Pi/autocontext proposes and repairs proof bodies; Lean is the correctness oracle.

## Status

- Published npm package. First trusted-publisher/provenance release: `pi-autocontext-lean-verify@0.1.4`.
- Tracks Linear issue `AC-731`.
- License: Apache-2.0.
- Default harness root in the standalone package: bundled `harness/` directory.
- `AUTOCONTEXT_FORMAL_ROOT` can override the harness root for local experiments.

## Install

From npm:

```bash
pi install npm:pi-autocontext-lean-verify
```

From a local checkout:

```bash
pi install ./pi-autocontext-lean-verify
```

Or test a local checkout for one run without installing:

```bash
pi -e ./pi-autocontext-lean-verify
```

If the package is moved away from the harness, set:

```bash
export AUTOCONTEXT_FORMAL_ROOT=/path/to/support/formal-proof-lean-pilot
```

The extension looks for Lean at:

```text
$LEAN
$AUTOCONTEXT_LEAN
/tmp/autocontext-elan-home/bin/lean
```

Autocontext is the repair engine and Lean is the oracle. Repair runs invoke the Python autocontext CLI on demand through:

```text
uvx --python 3.12 --from autocontext==0.4.8 autoctx improve ...
```

`action="preflight"` checks `uvx` and `autocontext==0.4.8` / `autoctx improve` availability so this dependency is explicit rather than a decorative package import.

Long-running run/benchmark/attribution actions default their result directories to a short temp path under the system temp directory (`pi-autocontext-lean-verify/...`) (or `$AUTOCONTEXT_LEAN_VERIFY_RESULTS_ROOT`) so npm-loaded extensions do not create overly long Pi session paths.

## Provided resources

- Extension tool: `autocontext_lean_verify`
- Skill: `lean-verify`
- Prompt template: `lean-verify.md`
- Fixture group registry: `fixture_groups.json`
- Domain model, validation matrix, proof-transfer benchmark, and repo split notes: `docs/DOMAIN.md`, `docs/VALIDATION.md`, `docs/PROOF_TRANSFER_BENCHMARK.md`, `docs/REPO_SPLIT.md`

## Tool actions

### Preflight

Checks harness paths, Lean, Python, manifest, and seed playbook.

```json
{
  "action": "preflight"
}
```

### Setup

Runs preflight and a minimal Lean smoke proof (`add_zero_right`). Use this after first installing or loading the package.

```json
{
  "action": "setup"
}
```

### Run

Runs `run_playbook_transfer.py` through a named mode. Use either explicit `fixtures` or a `fixtureGroup`.

```json
{
  "action": "run",
  "mode": "pre_repair_hint",
  "fixtureGroup": "broader",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 60
}
```

### Negative-control recovery

Use `maxAttempts=3` for the expanded negative-control group because `maxAttempts=2` showed provider variance while `maxAttempts=3` recovered all six fixtures in the latest probe.

```json
{
  "action": "run",
  "mode": "pre_repair_hint",
  "fixtureGroup": "negative_controls",
  "maxAttempts": 3,
  "rounds": 2,
  "timeoutSeconds": 60
}
```

### Benchmark

Runs the packaged proof-transfer benchmark: seeded autocontext/Pi vs direct Pi repair-loop on the same fixed Lean templates. The default fixture group is `challenge_v3_generalization`; pregeneration and synthetic hint candidates are disabled.

```json
{
  "action": "benchmark",
  "fixtureGroup": "challenge_v3_generalization",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

From a checkout, the same benchmark can be launched without Pi:

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
npm run benchmark:v20
npm run benchmark:v21
```

### Attribution

Runs seeded autocontext, unseeded isolated autocontext, and direct Pi repair-loop for attribution. The default fixture group is `challenge_v5_attribution`.

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v5_attribution",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

From a checkout:

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
npm run benchmark:v20
npm run benchmark:v21
```

### Summarize

Reads a saved run summary.

```json
{
  "action": "summarize",
  "runRoot": "results/20260506T_broader_fixture_baseline_comparison"
}
```

## Fixture groups

| Group               | Fixtures                                                                                                                                  |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `smoke`             | `add_zero_right`                                                                                                                          |
| `broader`           | Seven broader fixtures covering Nat distribution, Bool/List recursion, list helpers, tree helpers, and reverse/append.                    |
| `heldout`           | Seven original held-out transfer fixtures.                                                                                                |
| `combined`          | `broader` + `heldout` (`14` fixtures).                                                                                                    |
| `negative_controls` | Six fixtures: distribution, multiplication associativity/commutativity, addition cancellation, and filter length bound negative controls. |
| `challenge_v2_no_helper` | Three no-expected-proof fixtures requiring local helper lemma discovery. |
| `challenge_v3_generalization` | Four no-expected-proof theorem-generalization fixtures requiring accumulator/multi-helper proof plans. |
| `challenge_transfer` | All v2/v3 challenge fixtures (`7` fixtures). |
| `challenge_v4_count` | Four no-expected-proof count/list/tree fixtures. |
| `challenge_v5_attribution` | Four no-expected-proof fixtures for seeded/unseeded/direct attribution. |
| `challenge_v5_tree_tally` | The hard v5 tree/tally mirror fixture. |
| `challenge_v6_frontier` | Four no-expected-proof frontier fixtures where nested tree/partition composition starts separating seeded/unseeded/direct. |
| `challenge_v7_frontier` | Four no-expected-proof frontier-plus fixtures where seeded autocontext becomes unstable (`2/4`) while unseeded/direct are `0/4`. |
| `challenge_v8_diagnostics` | Four no-expected-proof diagnostic fixtures isolating the v7 partition-heavy accumulator failures into smaller raw-tree, keep/drop, and list reassembly components. |
| `challenge_v9_composition_gradient` | Six no-expected-proof composition-gradient fixtures splitting keep/drop partition-through-mirror into scalar and paired length/sum obligations. |
| `challenge_v10_stats_reification` | Six no-expected-proof statsAcc-reification fixtures isolating tuple normalization, metric extensionality, count metrics, and stats equality from metric hypotheses. |
| `challenge_v11_metric_composition` | Six no-expected-proof metric-composition fixtures combining keep/drop metric bundles with statsAcc extensionality boundaries. |
| `challenge_v12_simultaneous_metrics` | Seven no-expected-proof simultaneous-metric fixtures isolating keep/drop count-only, length-only, sum-only, pair, and triple metric bundles. |
| `challenge_v13_decomposition_order` | Six no-expected-proof fixtures isolating v12 triple-bundle ordering, append/filter sub-lemmas, tree-only metrics, and conjunction reassembly. |
| `challenge_v14_metric_order_permutations` | Six no-expected-proof fixtures covering all metric-order permutations for the full simultaneous keep/drop triple bundle. |
| `challenge_v15_proof_shape_hints` | Four no-expected-proof fixtures exposing metric-bundle, side-bundle, append/filter, and reassembly hypotheses for the hard length/count/sum order. |
| `challenge_v16_compact_reassembly_hints` | Four no-expected-proof fixtures replacing the large v15 reassembly hypothesis with compact generic/named packer hypotheses. |
| `challenge_v17_proof_plan_hints` | Four no-expected-proof fixtures adding harmless `True` proof-plan skeleton names to v16 compact packer shapes. |
| `challenge_v18_prompt_only_skeleton_hints` | Two no-expected-proof fixtures reusing v16 theorem statements while supplying detailed skeleton names only through seeded playbook context. |
| `challenge_v19_bare_skeleton_names` | Ablation over the two clean v18 fixtures using only bare skeleton-name bullets in the seeded playbook. |
| `challenge_v20_description_only_skeleton` | Ablation over the two clean v18 fixtures using compact skeleton descriptions without `plan_...` labels in the seeded playbook. |
| `challenge_v21_neutral_anchor_skeleton` | Ablation over the two clean v18 fixtures using neutral step anchors plus compact descriptions without `plan_...` labels in the seeded playbook. |
| `challenge_v22_code_like_anchor_skeleton` | Ablation over the two clean v18 fixtures using compact descriptions plus code-like snake_case anchors without the earlier detailed-plan prefix. |
| `challenge_v23_exact_labels_without_plan_prefix` | Ablation over the two clean v18 fixtures using the exact v18 detailed labels with only the prefix removed. |
| `challenge_v24_plan_prefix_generic_labels` | Ablation over the two clean v18 fixtures using compact descriptions plus generic `plan_` labels that differ from v18 exact labels. |
| `challenge_v25_step_prefix_exact_labels` | Ablation over the two clean v18 fixtures using compact descriptions plus `step_` prefixed exact v18 label roots. |
| `challenge_extended_transfer` | All v2/v3/v4/v5/v6/v7/v8/v9/v10/v11/v12/v13/v14/v15/v16/v17/v18 challenge fixtures (`78` fixtures). |

## Modes

| Mode                 | Behavior                                                                    |
| -------------------- | --------------------------------------------------------------------------- |
| `seeded_pregenerate` | Use verified playbook to pregenerate a proof, then Lean-check.              |
| `pre_repair_hint`    | No pregeneration; try verifier-checked candidates before primary Pi repair. |
| `post_repair_hint`   | No pregeneration; run primary Pi repair before hint candidates.             |
| `structured_retry`   | No pregeneration; structured alternate Pi retry without hint candidates.    |

Current strongest repair-only mode:

```text
pre_repair_hint
```

It maps to:

```text
--no-pregenerate
--structured-alternate-retry
--structured-hint-candidates
--pre-repair-hint-candidates
--max-attempts 2
--rounds 2
--timeout 60
```

## Frontier benchmark highlights

- v6 frontier: seeded `4/4`, unseeded `3/4`, direct `2/4`; hardest pattern was nested tree mirror + partition/count/length invariants.
- v7 frontier-plus: seeded `2/4`, unseeded `0/4`, direct `0/4`; repeated seeded-failed partition-heavy fixtures stayed `0/6`.
- v8 diagnostics: decomposing v7 gives seeded a clear edge but not full stability across repeats (`6/8` seeded, `1/8` unseeded, `0/8` direct); raw stats and list-only reassembly are stable, while keep/drop partition-through-mirror remains stochastic.
- v9 composition gradient: seeded solves all scalar/pair length+sum partition-through-mirror obligations (`6/6`), while unseeded solves `1/6` and direct `0/6`; the remaining frontier points toward `statsAcc` triple reification/composition rather than length/sum invariants themselves.
- v10 stats reification: seeded solves the full layer (`6/6`), unseeded solves core reification/count metrics (`3/6`), and direct solves only drop-count (`1/6`); the frontier is composing tuple normalization with metric equalities in the keep/drop tree-mirror setting.
- v11 metric composition: seeded solves `5/6`, unseeded `0/6`, direct `1/6`; the remaining seeded miss is the combined keep/drop metric-bundle proof, while applying provided metric bundles to `statsAcc` is comparatively easy.
- v12 simultaneous metrics: seeded solves all single-metric and two-metric simultaneous keep/drop bundles (`6/7` full suite); isolated repeats show the full count+length+sum bundle is stochastic for seeded (`1/3` across observations), while unseeded/direct have not solved it.
- v13 decomposition/order: seeded solves `5/6`, unseeded `0/6`, direct `1/6`; raw tree metrics, append/filter sub-lemmas, supplied append/filter hypotheses, side-grouped bundles, and conjunction reassembly all pass seeded. The only seeded miss is reordered full simultaneous metric grouping (`sum`, then `count`, then `length`), sharpening the frontier to conjunction ordering/grouping sensitivity.
- v14 metric-order permutations: seeded solves `5/6`, unseeded/direct `0/6`; canonical count/length/sum and v13's failed sum/count/length order both solve seeded, while length/count/sum misses. Focused seeded repeats put the v13 miss at `2/3` and the v14 miss at `2/3`, confirming stochastic/non-canonical conjunction-order sensitivity rather than a simple fixed order failure. A later focused budget probe showed `maxAttempts=3` with the same 120s Pi timeout produced only timeout-empty repairs (`0/3` for each miss). Raising timeout to 240s with the original `maxAttempts=2` recovers proofs but does not fully stabilize the frontier (`2/3` focused repeats for each miss; `3/4` each including the earlier timeout-240 smoke).
- v15 proof-shape hints: seeded solves `3/4`, unseeded `0/4`, direct `2/4`; metric/side reassembly is easy for direct, append/filter hypotheses let seeded solve the hard length/count/sum tree-induction shape, and the explicit reassembly-hyp variant misses in the full run. Focused repeats show append/filter hypotheses are stable seeded (`3/3`, `4/4` including original), while the larger explicit reassembly-hyp variant remains unstable (`1/3`, `1/4` including original). The frontier is not final conjunction assembly alone; compact helper hypotheses help more than large higher-order proof-shape hints.
- v16 compact reassembly hints: seeded solves `2/4`, unseeded/direct `0/4`; compact top-level Prop and generic Nat scalar packers solve in the full suite. The two first-run compact-packer misses each solve `2/3` on focused repeat (`2/4` including original), so compact packers reduce the v15 higher-order-hypothesis drag but do not remove stochastic induction/simp proof-search variance. Timeout 240 improves named-metric repeats to `3/3` but pair+top remains `2/3`, with severe wall-clock blowups despite Pi timeout messages, so it is not a clean stabilization knob.
- v17 proof-plan skeleton hints: seeded solves `4/4`, unseeded `0/4`, direct `1/4`; harmless `True` names expose the intended induction/by-cases/simp/add-normalization skeleton. Detailed plan names are stable on repeat (`3/3`, `4/4` including original for both packer shapes), while coarse plan names remain stochastic (`2/3`, `3/4` including original). This points to detailed skeleton naming as the missing prompt structure.
- v18 prompt-only skeleton hints: two clean v16 theorem-shape fixtures remove the v17 `True` plan hypotheses and move the same detailed skeleton names into the seeded playbook only. Seeded solves `2/2`, direct remains `0/2`, and seeded focused repeats are stable (`3/3` for both shapes, `4/4` including original). Unseeded is no longer zero (`1/2` attribution; repeats `1/3` pair+top and `1/3` named metric), so prompt-only skeleton context acts as a stabilizer rather than an exclusive capability source.
- v19 bare skeleton-name ablation: reuses the two clean v18 fixtures and swaps descriptive skeleton guidance for bare semantic labels only. Seeded solves `2/2` in the full attribution run, but repeats are unstable (`2/3` pair+top, `1/3` named metric; `3/4` and `2/4` including original). Unseeded is also stochastic (`0/3` pair+top, `1/3` named metric after a `2/2` full run), and direct remains `0/2`. Bare semantic labels alone do not reproduce v18 descriptive-context stabilization.
- v20 description-only skeleton ablation: reuses the two clean v18 fixtures and keeps compact natural-language skeleton descriptions while removing `plan_...` labels. Seeded solves `2/2` in the full attribution run, unseeded/direct solve `0/2`, but seeded repeats are only `2/3` for each fixture (`3/4` including original) because one repeat returns timeout-empty repairs for both fixtures. Descriptions alone are capable and stronger than bare labels on the named-metric shape, but they do not fully reproduce v18's descriptions+labels stabilization.
- v21 neutral-anchor skeleton ablation: reuses the two clean v18 fixtures and keeps compact descriptions with neutral natural-language step anchors instead of code-like `plan_...` labels. Seeded solves only `1/2` in the full attribution run, unseeded also solves `1/2`, and direct remains `0/2`. The first seeded repeat drops to `0/2` with severe wall-clock blowups; a partial second repeat fails pair+top before being curtailed. Neutral anchors do not close the v20-to-v18 stability gap and appear worse than description-only context in these probes.
- v22 code-like anchor skeleton ablation: reuses the two clean v18 fixtures and combines compact descriptions with snake_case step anchors that deliberately avoid the earlier detailed-plan prefix. Seeded solves `2/2` in attribution while unseeded/direct solve `0/2`, but seeded repeats are `2/3` for each fixture (`3/4` including attribution), matching v20-style partial stability rather than v18's stable `3/3`.
- v23 exact-label-minus-prefix ablation: reuses the two clean v18 fixtures and preserves v18's exact detailed labels with only the prefix removed. The first partial attribution attempt had seeded `1/2`; focused seeded retries were `2/2`, `0/2`, `2/2` (`2/3` per fixture), so removing only the prefix still fails to reproduce v18 stability.
- v24 generic plan-prefix ablation: reuses the two clean v18 fixtures and keeps the `plan_` prefix while changing to shorter generic labels. Focused seeded repeats were `1/2`, `1/2`, `2/2` (`2/3` per fixture), so generic `plan_` labels do not reproduce v18 stability.
- v25 step-prefix exact-label ablation: reuses the two clean v18 fixtures, preserves the exact v18 semantic label roots, and replaces the original prefix with `step_`. Focused seeded repeats were `1/2`, `0/2`, `2/2` (pair+top `2/3`, named metric `1/3`), so alternate-prefixed exact roots do not reproduce v18 stability.

See `docs/V6_FRONTIER_REPORT.md`, `docs/V7_FRONTIER_REPORT.md`, `docs/V8_DIAGNOSTIC_REPORT.md`, `docs/V9_COMPOSITION_GRADIENT_REPORT.md`, `docs/V10_STATS_REIFICATION_REPORT.md`, `docs/V11_METRIC_COMPOSITION_REPORT.md`, `docs/V12_SIMULTANEOUS_METRICS_REPORT.md`, `docs/V13_DECOMPOSITION_ORDER_REPORT.md`, `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md`, `docs/V15_PROOF_SHAPE_HINTS_REPORT.md`, `docs/V16_COMPACT_REASSEMBLY_HINTS_REPORT.md`, `docs/V17_PROOF_PLAN_HINTS_REPORT.md`, `docs/V18_PROMPT_ONLY_SKELETON_HINTS_REPORT.md`, `docs/V19_BARE_SKELETON_NAMES_REPORT.md`, `docs/V20_DESCRIPTION_ONLY_SKELETON_REPORT.md`, `docs/V21_NEUTRAL_ANCHOR_SKELETON_REPORT.md`, `docs/V22_CODE_LIKE_ANCHOR_SKELETON_REPORT.md`, `docs/V23_EXACT_LABELS_WITHOUT_PLAN_PREFIX_REPORT.md`, `docs/V24_PLAN_PREFIX_GENERIC_LABELS_REPORT.md`, and `docs/V25_STEP_PREFIX_EXACT_LABELS_REPORT.md`.

## Guardrails

The underlying harness requires:

- fixed theorem templates
- proof-body-only candidates
- no `sorry`
- no `admit`
- no new axioms
- no `unsafe`
- no theorem weakening
- no new imports
- Lean verification before success is counted

## Local validation

The local package has been smoke-tested through Pi:

```bash
pi -e ./pi-autocontext-lean-verify --no-session --no-builtin-tools --tools autocontext_lean_verify -p 'Use autocontext_lean_verify with action="preflight"'
```

Observed preflight summary:

```text
Lean version: 4.29.1
Python: 3.14.2
uvx: uv-tool-uvx 0.6.17
Autocontext runtime: autocontext==0.4.8 via uvx autoctx improve (ok)
Fixture count: 130
Fixture groups: smoke=1, broader=7, heldout=7, combined=14, negative_controls=6, challenge_v2_no_helper=3, challenge_v3_generalization=4, challenge_transfer=7, challenge_v4_count=4, challenge_v5_attribution=4, challenge_v5_tree_tally=1, challenge_v6_frontier=4, challenge_v7_frontier=4, challenge_v8_diagnostics=4, challenge_v9_composition_gradient=6, challenge_v10_stats_reification=6, challenge_v11_metric_composition=6, challenge_v12_simultaneous_metrics=7, challenge_v13_decomposition_order=6, challenge_v14_metric_order_permutations=6, challenge_v15_proof_shape_hints=4, challenge_v16_compact_reassembly_hints=4, challenge_v17_proof_plan_hints=4, challenge_v18_prompt_only_skeleton_hints=2, challenge_v19_bare_skeleton_names=2, challenge_v20_description_only_skeleton=2, challenge_v21_neutral_anchor_skeleton=2, challenge_v22_code_like_anchor_skeleton=2, challenge_v23_exact_labels_without_plan_prefix=2, challenge_v24_plan_prefix_generic_labels=2, challenge_v25_step_prefix_exact_labels=2, challenge_extended_transfer=78
```

A zero-Pi-call run smoke test was completed:

```text
results/20260506T_pi_package_wrapper_smoke_add_zero
1 / 1 proved
Pi calls: 0
Lean attempts: 1
```

A nontrivial package-driven run was also completed on a distribution negative-control fixture:

```text
results/20260506T_pi_package_wrapper_nontrivial_mul_add
1 / 1 proved
Pi calls: 1
Lean attempts: 6
Pre-repair hint generated/passed/used: 3/0/0
```

This confirms that Lean-rejected synthetic candidates fall back to primary Pi repair through the package wrapper.

The expanded negative-control group now contains six fixtures. In no-pregeneration probes, all generated synthetic hint candidates were Lean-rejected (`45 / 45` failed across three runs). With `maxAttempts=3`, primary Pi repair recovered `6 / 6` fixtures after those candidate rejections.

Post-registry package-driven validation also passed through the `autocontext_lean_verify` tool:

```text
results/20260506T_pi_package_registry_setup_smoke
1 / 1 proved, Pi calls: 0, Lean attempts: 1

results/20260506T_pi_package_registry_negative_controls_attempts3
6 / 6 proved, Pi calls: 7, Lean attempts: 33, pre-repair hints: 15/0/15/0

results/20260506T_pi_package_registry_combined_seeded
14 / 14 proved, Pi calls: 14, Lean attempts: 17, pre-repair hints: 2/1/1
```

The npm-published trusted-publisher release was smoke-tested from the registry with:

```bash
pi -e npm:pi-autocontext-lean-verify@0.1.4 --no-context-files --no-builtin-tools --tools autocontext_lean_verify -p 'Call autocontext_lean_verify with action="setup"'
```

Observed npm-installed setup result:

```text
1 / 1 proved
Pi calls: 0
Lean verifier attempts: 1
Package source: npm:pi-autocontext-lean-verify@0.1.4
```

`npm pack --dry-run --json` includes runtime package assets and the bundled harness, while excluding tests and generated result artifacts.


## Proof-transfer benchmark evidence

Version `0.1.6` added packaged v2/v3 no-expected-proof challenge fixtures and a reproducible benchmark command. Version `0.1.7` adds v4/v5 challenge fixtures plus attribution benchmarking. The local v3 repeated stability probe produced:

```text
seeded autocontext: 12 / 12 proofs across 3 trials
direct Pi repair-loop: 7 / 12 proofs across 3 trials
hard-plus subset: seeded autocontext 6 / 6 vs direct Pi 1 / 6
```

The v4/v5 follow-up produced:

```text
v4 seeded autocontext: 12 / 12 across 3 repeats
v4 direct Pi repair-loop: 3 / 12 across 3 repeats
v5 seeded autocontext: 4 / 4 full set; hard tree/tally 3 / 3
v5 unseeded isolated: 3 / 4 full set; hard tree/tally 1 / 3
v5 direct Pi repair-loop: 1 / 4 full set; hard tree/tally 0 / 3
```

See `docs/PROOF_TRANSFER_BENCHMARK.md` for fixture groups, commands, and interpretation.

## Release

Version `0.1.0` was the initial experimental npm release. Version `0.1.4` was the first successful GitHub OIDC trusted-publisher release with npm provenance attestations. Version `0.1.6` promotes the v2/v3 challenge fixtures and proof-transfer benchmark runner. Version `0.1.7` promotes the v4/v5 fixtures plus attribution benchmarking. Version `0.1.8` fixes default benchmark run roots for npm-loaded extensions to avoid Pi session `ENAMETOOLONG` failures. Version `0.1.9` promotes the v6/v7 frontier fixtures and reports. Version `0.1.10` promotes the v8-v12 diagnostic/frontier fixtures and reports. Version `0.1.11` promotes v13/v14 order-sensitivity fixtures, timeout/process-group attribution robustness, and budget-vs-timeout frontier evidence. Version `0.1.12` promotes v15 proof-shape hint diagnostics and focused stability evidence for compact helper hypotheses versus large explicit reassembly hints. Version `0.1.13` promotes v16/v17 diagnostics: compact reassembly packers, timeout-240 caveats, and detailed proof-plan skeleton hints. Version `0.1.14` promotes v18/v19/v20 prompt-only ablations over detailed descriptions, bare labels, and description-only skeleton context. Version `0.1.15` promotes v21 neutral-anchor skeleton evidence and hardens subprocess process-group timeout cleanup plus short temp run roots for run/benchmark/attribution actions. Unpublished attempts `0.1.1`–`0.1.3` do not exist in the npm registry.

`0.1.11` was published through GitHub trusted publishing from tag `v0.1.11` (workflow `25753534079`), had two npm provenance attestations, and was registry-smoked with setup `1/1` plus a v14 timeout-240 attribution contrast: seeded `1/1`, unseeded `0/1`, direct `0/1`.

`0.1.12` was published through GitHub trusted publishing from tag `v0.1.12` (workflow `25761371690`), has two npm provenance attestations, and was registry-smoked with setup `1/1` over 120 fixtures plus a focused v15 append/filter-hypothesis attribution contrast: seeded `1/1`, unseeded `0/1`, direct `0/1`.

`0.1.13` was published through GitHub trusted publishing from tag `v0.1.13` (workflow `25774592204`), has two npm provenance attestations, and was registry-smoked with setup `1/1` over 128 fixtures plus a focused v17 detailed proof-plan attribution contrast: seeded `1/1`, unseeded `0/1`, direct `0/1`.

`0.1.14` was published through GitHub trusted publishing from tag `v0.1.14` (workflow `25813274000`), has two npm provenance attestations, and was registry-smoked with setup `1/1` over 130 fixtures plus a focused v20 description-only seeded timeout-240 smoke: seeded `1/1`.

`0.1.15` was published through GitHub trusted publishing from tag `v0.1.15` (workflow `25838541595`), is npm `latest`, has two npm provenance attestations, and includes the process-group timeout/short-run-root hardening required before v22 prompt-transfer stress tests. Registry smoke covered preflight, setup `1/1`, default `action="run"` short temp-root behavior, and packaged `process_utils.py` process-group cleanup. The source tree after `0.1.15` adds v22 code-like snake_case anchor fixtures, v23 exact-label-minus-prefix fixtures, v24 generic plan-prefix fixtures, v25 step-prefix exact-label fixtures, and a second timeout hardening patch that bounds post-kill waits and force-closes leaked subprocess pipes.

Future releases use GitHub's npm trusted publisher workflow on version tags:

```text
.github/workflows/publish.yml
on: push tags v*
environment: publish-pi-autocontext-lean-verify
npm publish --provenance --access public
```

Before cutting the next release:

- keep CI green,
- bump `package.json` version,
- push tag `v<version>`,
- approve the `publish-pi-autocontext-lean-verify` environment gate,
- verify npm publication and provenance attestations, then create/update GitHub release notes.
