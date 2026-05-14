# Formal Proof Package Validation Matrix

This matrix records the durable evidence currently supporting `pi-autocontext-lean-verify` as an experimental Pi package.

Lean remains the oracle: a row counts only if the final proof body was checked against the unchanged Lean template.

| Claim                                                      |                    Evidence | Artifact                                                                                          |
| ---------------------------------------------------------- | --------------------------: | ------------------------------------------------------------------------------------------------- |
| Harness sanity: every expected proof still verifies        | 52 / 52 expected-proof fixtures (130 manifest fixtures) | `benchmark_manifest.json` plus fixture `expected_proof.lean` checks                               |
| Package setup works through Pi                             |           1 / 1 smoke proof | `results/20260506T_pi_package_setup_action_smoke`                                                 |
| Post-registry package setup works through Pi               |           1 / 1 smoke proof | `results/20260506T_pi_package_registry_setup_smoke`                                               |
| Package fixture groups work through Pi                     |           1 / 1 smoke proof | `results/20260506T_pi_package_fixture_group_smoke`                                                |
| Combined broader + held-out transfer stability             |      42 / 42 fixture-trials | `results/20260506T_combined_broader_heldout_pre_repair_hint_variance`                             |
| Post-registry package combined run                         |              14 / 14 proved | `results/20260506T_pi_package_registry_combined_seeded`                                           |
| Synthetic hints are rejected on expanded negative controls | 45 / 45 candidates rejected | `results/20260506T_expanded_negative_control_probe`                                               |
| Post-registry package negative-control rejection           | 15 / 15 candidates rejected | `results/20260506T_pi_package_registry_negative_controls_attempts3`                               |
| Negative controls recover with larger fallback budget      |              6 / 6 fixtures | `results/20260506T_expanded_negative_controls_pre_repair_hint_no_pregenerate_attempts3_timeout60` |
| Post-registry package negative-control recovery            |              6 / 6 fixtures | `results/20260506T_pi_package_registry_negative_controls_attempts3`                               |
| Challenge v2 no-helper repeated stability                  |      18 / 18 fixture-trials | `results/20260507T_challenge_v2_repeated_stability_report.md`                                     |
| Challenge v3 theorem-generalization seeded stability       |      12 / 12 fixture-trials | `results/20260507T_challenge_v3_repeated_stability_report.md`                                     |
| Challenge v3 direct-repair baseline contrast               |       7 / 12 fixture-trials | `results/20260507T_challenge_v3_repeated_stability_report.md`                                     |
| Packaged v3 benchmark command sanity run                   |   seeded 4 / 4; direct 4 / 4 | `harness/results/20260509T190246Z_proof_transfer_benchmark_challenge_v3_generalization`            |
| Challenge v4 seeded stability                            |      12 / 12 fixture-trials | `results/20260510T_challenge_v4_stability_attribution_report.md`                                 |
| Challenge v4 direct-repair baseline contrast              |       3 / 12 fixture-trials | `results/20260510T_challenge_v4_stability_attribution_report.md`                                 |
| Challenge v5 seeded full-set attribution                  |               4 / 4 proofs | `results/20260510T_challenge_v5_attribution_report.md`                                           |
| Challenge v5 unseeded full-set attribution                |               3 / 4 proofs | `results/20260510T_challenge_v5_attribution_report.md`                                           |
| Challenge v5 hard tree/tally seeded stability             |               3 / 3 proofs | `results/20260510T_challenge_v5_attribution_report.md`                                           |
| Challenge v5 hard tree/tally unseeded contrast            |               1 / 3 proofs | `results/20260510T_challenge_v5_attribution_report.md`                                           |
| Challenge v6 seeded frontier attribution                |               4 / 4 proofs | `docs/V6_FRONTIER_REPORT.md`                                                                      |
| Challenge v6 unseeded frontier contrast                |               3 / 4 proofs | `docs/V6_FRONTIER_REPORT.md`                                                                      |
| Challenge v6 direct frontier contrast                  |               2 / 4 proofs | `docs/V6_FRONTIER_REPORT.md`                                                                      |
| Challenge v7 seeded frontier-plus attribution          |               2 / 4 proofs | `docs/V7_FRONTIER_REPORT.md`                                                                      |
| Challenge v7 unseeded/direct frontier-plus contrast    |               0 / 4 proofs | `docs/V7_FRONTIER_REPORT.md`                                                                      |
| Challenge v7 seeded-failed stability                   |               0 / 6 proofs | `docs/V7_FRONTIER_REPORT.md`                                                                      |
| Challenge v8 diagnostic fixtures have local Lean witnesses |      4 / 4 fixture templates | `docs/V8_DIAGNOSTIC_REPORT.md`                                                                    |
| Challenge v8 first seeded diagnostic probe             |               4 / 4 proofs | `docs/V8_DIAGNOSTIC_REPORT.md`                                                                    |
| Challenge v8 seeded diagnostic repeat                  |               2 / 4 proofs | `docs/V8_DIAGNOSTIC_REPORT.md`                                                                    |
| Challenge v8 combined diagnostic attribution           |     seeded 6 / 8; unseeded 1 / 8; direct 0 / 8 | `docs/V8_DIAGNOSTIC_REPORT.md`                                                                    |
| Challenge v9 composition-gradient fixtures have local Lean witnesses |      6 / 6 fixture templates | `docs/V9_COMPOSITION_GRADIENT_REPORT.md`                                                         |
| Challenge v9 seeded composition-gradient attribution   |               6 / 6 proofs | `docs/V9_COMPOSITION_GRADIENT_REPORT.md`                                                         |
| Challenge v9 unseeded/direct composition-gradient contrast |     unseeded 1 / 6; direct 0 / 6 | `docs/V9_COMPOSITION_GRADIENT_REPORT.md`                                                         |
| Challenge v10 stats-reification fixtures have local Lean witnesses |      6 / 6 fixture templates | `docs/V10_STATS_REIFICATION_REPORT.md`                                                           |
| Challenge v10 seeded stats-reification attribution     |               6 / 6 proofs | `docs/V10_STATS_REIFICATION_REPORT.md`                                                           |
| Challenge v10 unseeded/direct stats-reification contrast |     unseeded 3 / 6; direct 1 / 6 | `docs/V10_STATS_REIFICATION_REPORT.md`                                                           |
| Challenge v11 metric-composition fixtures have local Lean witnesses |      6 / 6 fixture templates | `docs/V11_METRIC_COMPOSITION_REPORT.md`                                                           |
| Challenge v11 seeded metric-composition attribution    |               5 / 6 proofs | `docs/V11_METRIC_COMPOSITION_REPORT.md`                                                           |
| Challenge v11 unseeded/direct metric-composition contrast |     unseeded 0 / 6; direct 1 / 6 | `docs/V11_METRIC_COMPOSITION_REPORT.md`                                                           |
| Challenge v12 simultaneous-metric fixtures have local Lean witnesses |      7 / 7 fixture templates | `docs/V12_SIMULTANEOUS_METRICS_REPORT.md`                                                         |
| Challenge v12 seeded simultaneous-metric attribution   |               6 / 7 proofs | `docs/V12_SIMULTANEOUS_METRICS_REPORT.md`                                                         |
| Challenge v12 triple-bundle seeded stability           |   1 / 3 observations | `docs/V12_SIMULTANEOUS_METRICS_REPORT.md`                                                         |
| Challenge v12 unseeded/direct simultaneous-metric contrast |     unseeded 0 / 7; direct 0 / 7 | `docs/V12_SIMULTANEOUS_METRICS_REPORT.md`                                                         |
| Challenge v13 decomposition/order fixtures have local Lean witnesses |      6 / 6 fixture templates | `docs/V13_DECOMPOSITION_ORDER_REPORT.md`                                                          |
| Challenge v13 seeded decomposition/order attribution      |               5 / 6 proofs | `docs/V13_DECOMPOSITION_ORDER_REPORT.md`                                                          |
| Challenge v13 unseeded/direct decomposition/order contrast |     unseeded 0 / 6; direct 1 / 6 | `docs/V13_DECOMPOSITION_ORDER_REPORT.md`                                                          |
| Attribution timeout/process-group robustness patch         | subprocess group cleanup and scaled budgets | `docs/V13_DECOMPOSITION_ORDER_REPORT.md`                                                          |
| Challenge v14 metric-order permutation fixtures have local Lean witnesses |      6 / 6 fixture templates | `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md`                                                    |
| Challenge v14 seeded metric-order attribution             |               5 / 6 proofs | `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md`                                                    |
| Challenge v14 unseeded/direct metric-order contrast       |     unseeded 0 / 6; direct 0 / 6 | `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md`                                                    |
| Challenge v13/v14 order-sensitive seeded repeats          |     2 / 3 each focused miss | `docs/V13_DECOMPOSITION_ORDER_REPORT.md`, `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md`          |
| Challenge v13/v14 attempt-budget probe at timeout 120     |     0 / 3 each focused miss | `docs/V13_DECOMPOSITION_ORDER_REPORT.md`, `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md`          |
| Challenge v13/v14 timeout-240 focused probe               |     1 / 1 each focused miss | `docs/V13_DECOMPOSITION_ORDER_REPORT.md`, `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md`          |
| Challenge v13/v14 timeout-240 focused repeats             |     2 / 3 each focused miss; 3 / 4 including smoke | `docs/V13_DECOMPOSITION_ORDER_REPORT.md`, `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md`          |
| Challenge v15 proof-shape hint fixtures have local Lean witnesses |      4 / 4 fixture templates | `docs/V15_PROOF_SHAPE_HINTS_REPORT.md`                                                            |
| Challenge v15 seeded proof-shape attribution              |               3 / 4 proofs | `docs/V15_PROOF_SHAPE_HINTS_REPORT.md`                                                            |
| Challenge v15 unseeded/direct proof-shape contrast        |     unseeded 0 / 4; direct 2 / 4 | `docs/V15_PROOF_SHAPE_HINTS_REPORT.md`                                                            |
| Challenge v15 focused seeded stability                    |     append/filter hyps 3 / 3; explicit reassembly hyp 1 / 3 | `docs/V15_PROOF_SHAPE_HINTS_REPORT.md`                                                            |
| Challenge v16 compact reassembly fixtures have local Lean witnesses |      4 / 4 fixture templates | `docs/V16_COMPACT_REASSEMBLY_HINTS_REPORT.md`                                                     |
| Challenge v16 seeded compact reassembly attribution        |               2 / 4 proofs | `docs/V16_COMPACT_REASSEMBLY_HINTS_REPORT.md`                                                     |
| Challenge v16 unseeded/direct compact reassembly contrast  |     unseeded 0 / 4; direct 0 / 4 | `docs/V16_COMPACT_REASSEMBLY_HINTS_REPORT.md`                                                     |
| Challenge v16 focused seeded miss repeats                  |     pair+top 2 / 3; named metric 2 / 3 | `docs/V16_COMPACT_REASSEMBLY_HINTS_REPORT.md`                                                     |
| Challenge v16 timeout-240 focused repeats                  |     pair+top 2 / 3; named metric 3 / 3; severe wall-clock blowups | `docs/V16_COMPACT_REASSEMBLY_HINTS_REPORT.md`                                                     |
| Challenge v17 proof-plan hint fixtures have local Lean witnesses |      4 / 4 fixture templates | `docs/V17_PROOF_PLAN_HINTS_REPORT.md`                                                             |
| Challenge v17 seeded proof-plan attribution                |               4 / 4 proofs | `docs/V17_PROOF_PLAN_HINTS_REPORT.md`                                                             |
| Challenge v17 unseeded/direct proof-plan contrast          |     unseeded 0 / 4; direct 1 / 4 | `docs/V17_PROOF_PLAN_HINTS_REPORT.md`                                                             |
| Challenge v17 seeded stability repeats                    |     detailed 3 / 3 each; coarse 2 / 3 each | `docs/V17_PROOF_PLAN_HINTS_REPORT.md`                                                             |
| Challenge v18 prompt-only skeleton fixtures have local Lean witnesses |      2 / 2 fixture templates | `docs/V18_PROMPT_ONLY_SKELETON_HINTS_REPORT.md`                                                   |
| Challenge v18 initial `rfl` rejection                      |      2 / 2 fixture templates | `docs/V18_PROMPT_ONLY_SKELETON_HINTS_REPORT.md`                                                   |
| Challenge v18 prompt-only seeded attribution               |               2 / 2 proofs | `docs/V18_PROMPT_ONLY_SKELETON_HINTS_REPORT.md`                                                    |
| Challenge v18 unseeded/direct prompt-only contrast         |     unseeded 1 / 2; direct 0 / 2 | `docs/V18_PROMPT_ONLY_SKELETON_HINTS_REPORT.md`                                                   |
| Challenge v18 prompt-only stability repeats                |     seeded 3 / 3 each; unseeded 1 / 3 each | `docs/V18_PROMPT_ONLY_SKELETON_HINTS_REPORT.md`                                                   |
| Challenge v19 bare-name ablation setup                     |      2 clean reused fixtures | `docs/V19_BARE_SKELETON_NAMES_REPORT.md`                                                          |
| Challenge v19 bare-name attribution                        |     seeded 2 / 2; unseeded 2 / 2; direct 0 / 2 | `docs/V19_BARE_SKELETON_NAMES_REPORT.md`                                             |
| Challenge v19 bare-name stability repeats                  |     seeded pair+top 2 / 3; seeded named metric 1 / 3 | `docs/V19_BARE_SKELETON_NAMES_REPORT.md`                                      |
| Challenge v20 description-only ablation setup              |      2 clean reused fixtures | `docs/V20_DESCRIPTION_ONLY_SKELETON_REPORT.md`                                                    |
| Challenge v20 description-only attribution                  |     seeded 2 / 2; unseeded 0 / 2; direct 0 / 2 | `docs/V20_DESCRIPTION_ONLY_SKELETON_REPORT.md`                                      |
| Challenge v20 description-only stability repeats            |     seeded 2 / 3 each; unseeded pair+top 2 / 3; unseeded named metric 1 / 3 | `docs/V20_DESCRIPTION_ONLY_SKELETON_REPORT.md`              |
| Challenge v21 neutral-anchor ablation setup                 |      2 clean reused fixtures | `docs/V21_NEUTRAL_ANCHOR_SKELETON_REPORT.md`                                                     |
| Challenge v21 neutral-anchor attribution                     |     seeded 1 / 2; unseeded 1 / 2; direct 0 / 2 | `docs/V21_NEUTRAL_ANCHOR_SKELETON_REPORT.md`                                      |
| Challenge v21 neutral-anchor focused probes                  |     seeded repeat 0 / 2; partial second seeded repeat failed pair+top; severe wall-clock blowups | `docs/V21_NEUTRAL_ANCHOR_SKELETON_REPORT.md` |
| Challenge v22 code-like-anchor ablation setup                |      2 clean reused fixtures | `harness/playbooks/challenge_v22_code_like_anchor_skeleton_v1.md`                              |
| Default run/benchmark/attribution roots avoid npm temp path ENAMETOOLONG | short temp result paths by default | `action="run"`, `action="benchmark"`, and `action="attribution"` defaults use temp roots |
| Harness timeout cleanup kills child process groups          | tracked process groups + SIGTERM/SIGKILL cleanup | `harness/process_utils.py`, `tests/package_validation.py`                                        |
| Package dry-run excludes result artifacts and tests        |  runtime package files only | `npm pack --dry-run --json`                                                                       |
| Release `0.1.11` candidate contents                       |  v13/v14 fixtures + timeout robustness | `package.json`, `docs/V13_DECOMPOSITION_ORDER_REPORT.md`, `docs/V14_METRIC_ORDER_PERMUTATIONS_REPORT.md` |
| Release `0.1.11` trusted publish                          |  npm latest + 2 attestations | `v0.1.11`, workflow `25753534079`, npm attestations endpoint                                      |
| Release `0.1.12` candidate contents                       |  v15 fixtures + proof-shape stability evidence | `package.json`, `docs/V15_PROOF_SHAPE_HINTS_REPORT.md`                                           |
| Release `0.1.12` trusted publish                          |  npm latest + 2 attestations | `v0.1.12`, workflow `25761371690`, npm attestations endpoint                                      |
| Release `0.1.13` candidate contents                       |  v16/v17 fixtures + proof-plan skeleton evidence | `package.json`, `docs/V16_COMPACT_REASSEMBLY_HINTS_REPORT.md`, `docs/V17_PROOF_PLAN_HINTS_REPORT.md` |
| Release `0.1.13` trusted publish                          |  npm latest + 2 attestations | `v0.1.13`, workflow `25774592204`, npm attestations endpoint                                      |
| Release `0.1.14` candidate contents                       |  v18/v19/v20 prompt-only skeleton ablation fixtures + reports | `package.json`, `docs/V18_PROMPT_ONLY_SKELETON_HINTS_REPORT.md`, `docs/V19_BARE_SKELETON_NAMES_REPORT.md`, `docs/V20_DESCRIPTION_ONLY_SKELETON_REPORT.md` |
| Release `0.1.14` trusted publish                          |  npm latest + 2 attestations | `v0.1.14`, workflow `25813274000`, npm attestations endpoint                                      |
| Release `0.1.15` candidate contents                       |  v21 neutral-anchor skeleton ablation + process-group timeout/short-run-root hardening | `package.json`, `harness/process_utils.py`, `docs/V21_NEUTRAL_ANCHOR_SKELETON_REPORT.md` |
| Release `0.1.15` trusted publish                          | npm latest + 2 attestations | `v0.1.15`, workflow `25838541595`, npm attestations endpoint                                      |
| Registry-installed `0.1.15` preflight smoke                | autocontext runtime ok; 130 fixtures; 28 groups through v21 | `/tmp/pi-0.1.15-preflight-smoke.log` |
| Registry-installed `0.1.15` setup smoke                    | 1 / 1 proof; 130 fixtures | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-extensions/npm/f35b2129/node_modules/pi-autocontext-lean-verify/harness/results/pi_package_setup_20260514T025015` |
| Registry-installed `0.1.15` default run-root smoke         | `action="run"` without explicit `runRoot` used short temp root; 1 / 1 proof | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260514T025132_run_pre_repair_hint` |
| Registry-installed `0.1.15` process cleanup smoke          | timeout exit 124; marker preserved; spawned child process gone | packaged `harness/process_utils.py` from npm install |
| Registry-installed `0.1.14` setup smoke                    |  1 / 1 proof; 130 fixtures | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-extensions/npm/f35b2129/node_modules/pi-autocontext-lean-verify/harness/results/pi_package_setup_20260513T165025` |
| Registry-installed `0.1.14` v20 timeout-120 attribution probes | seeded 0 / 1 timeout-empty on pair+top and named-metric single-fixture probes | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260513T165143_attribution_challenge_v20_description_only_skeleton`, `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260513T165856_attribution_challenge_v20_description_only_skeleton` |
| Registry-installed `0.1.14` v20 seeded timeout-240 smoke   |  seeded 1 / 1; Pi elapsed 194.13s | `/tmp/pi-0.1.14-v20-seeded-timeout240-20260513T172054Z`                                |
| Registry-installed `0.1.14` v20 attribution timeout-240 smoke | seeded 1 / 1; unseeded 0 / 1; direct 1 / 1 | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260513T170558_attribution_challenge_v20_description_only_skeleton` |
| Registry-installed `0.1.13` setup smoke                    |  1 / 1 proof; 128 fixtures | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-extensions/npm/f35b2129/node_modules/pi-autocontext-lean-verify/harness/results/pi_package_setup_20260513T023355` |
| Registry-installed `0.1.13` v17 detailed-plan attribution smoke | seeded 1 / 1; unseeded 0 / 1; direct 0 / 1 | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260513T023428_attribution_challenge_v17_proof_plan_hints` |
| Registry-installed `0.1.12` setup smoke                    |  1 / 1 proof; 120 fixtures | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-extensions/npm/f35b2129/node_modules/pi-autocontext-lean-verify/harness/results/pi_package_setup_20260512T205217` |
| Registry-installed `0.1.12` v15 append/filter attribution smoke | seeded 1 / 1; unseeded 0 / 1; direct 0 / 1 | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260512T205258_attribution_challenge_v15_proof_shape_hints` |
| Registry-installed `0.1.11` setup smoke                    |  1 / 1 proof; 116 fixtures; Lean 4.29.1 | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-extensions/npm/f35b2129/node_modules/pi-autocontext-lean-verify/harness/results/pi_package_setup_20260512T181956` |
| Registry-installed `0.1.11` v14 timeout-240 attribution smoke | seeded 1 / 1; unseeded 0 / 1; direct 0 / 1 | `/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260512T182026_attribution_challenge_v14_metric_order_permutations` |

## Runtime dependency contract

This package is a Pi wrapper around an autocontext Lean verification harness. The TypeScript extension imports Pi runtime modules from `@earendil-works/*`; the proof-repair harness invokes autocontext as an on-demand Python CLI runtime:

```text
uvx --python 3.12 --from autocontext==0.4.8 autoctx improve ...
```

Preflight checks both `uvx` and `autocontext==0.4.8` / `autoctx improve` availability. This keeps autocontext as the real repair-engine dependency while Lean remains the proof oracle.

Run, benchmark, and attribution actions default to the system temp directory (`pi-autocontext-lean-verify/...`) (or `$AUTOCONTEXT_LEAN_VERIFY_RESULTS_ROOT`) instead of package-internal `harness/results/...` when `runRoot` is omitted. This avoids long npm temp paths causing Pi session `ENAMETOOLONG` failures.

## Recommended package-level checks

Run these after package changes:

```bash
python3 -m unittest test_pi_autocontext_lean_verify_package.py
pi -e ./pi-autocontext-lean-verify --no-session --no-builtin-tools --tools autocontext_lean_verify -p 'Use autocontext_lean_verify with action="preflight"'
cd pi-autocontext-lean-verify && npm pack --dry-run --json
```

Post-registry package-driven acceptance checks:

```json
{
  "action": "setup",
  "runRoot": "results/20260506T_pi_package_registry_setup_smoke"
}
```

For negative-control recovery through the package, prefer `maxAttempts=3`:

```json
{
  "action": "run",
  "mode": "pre_repair_hint",
  "fixtureGroup": "negative_controls",
  "maxAttempts": 3,
  "rounds": 2,
  "timeoutSeconds": 60,
  "runRoot": "results/20260506T_pi_package_registry_negative_controls_attempts3"
}
```

For combined seeded transfer through the package registry:

```json
{
  "action": "run",
  "mode": "seeded_pregenerate",
  "fixtureGroup": "combined",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 60,
  "runRoot": "results/20260506T_pi_package_registry_combined_seeded"
}
```

For the packaged proof-transfer benchmark:

```json
{
  "action": "benchmark",
  "fixtureGroup": "challenge_v3_generalization",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

Equivalent checkout commands:

```bash
npm run benchmark:v3
npm run benchmark:v4
npm run benchmark:v5
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

For seeded/unseeded/direct attribution through Pi:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v5_attribution",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

## Interpretation

- `combined` validates transfer stability across broader and held-out fixtures.
- `negative_controls` validates safety: generated candidates are useful only when Lean accepts them; rejected candidates are discarded and Pi repair remains the fallback.
- Current evidence supports an experimental package, not a general theorem prover claim.
