# Formal Proof Package Validation Matrix

This matrix records the durable evidence currently supporting `pi-autocontext-lean-verify` as an experimental Pi package.

Lean remains the oracle: a row counts only if the final proof body was checked against the unchanged Lean template.

| Claim                                                      |                    Evidence | Artifact                                                                                          |
| ---------------------------------------------------------- | --------------------------: | ------------------------------------------------------------------------------------------------- |
| Harness sanity: every expected proof still verifies        | 52 / 52 expected-proof fixtures (110 manifest fixtures) | `benchmark_manifest.json` plus fixture `expected_proof.lean` checks                               |
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
| Default benchmark run roots avoid npm temp path ENAMETOOLONG | short temp result paths by default | `action="attribution"` npm smoke without explicit `runRoot`                                      |
| Package dry-run excludes result artifacts and tests        |  runtime package files only | `npm pack --dry-run --json`                                                                       |

## Runtime dependency contract

This package is a Pi wrapper around an autocontext Lean verification harness. The TypeScript extension imports Pi runtime modules from `@earendil-works/*`; the proof-repair harness invokes autocontext as an on-demand Python CLI runtime:

```text
uvx --python 3.12 --from autocontext==0.4.8 autoctx improve ...
```

Preflight checks both `uvx` and `autocontext==0.4.8` / `autoctx improve` availability. This keeps autocontext as the real repair-engine dependency while Lean remains the proof oracle.

Benchmark and attribution actions default to `the system temp directory (`pi-autocontext-lean-verify/...`)/...` (or `$AUTOCONTEXT_LEAN_VERIFY_RESULTS_ROOT`) instead of package-internal `harness/results/...` when `runRoot` is omitted. This avoids long npm temp paths causing Pi session `ENAMETOOLONG` failures.

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
