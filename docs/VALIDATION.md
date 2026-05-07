# Formal Proof Package Validation Matrix

This matrix records the durable evidence currently supporting `pi-autocontext-lean-verify` as an experimental Pi package.

Lean remains the oracle: a row counts only if the final proof body was checked against the unchanged Lean template.

| Claim                                                      |                    Evidence | Artifact                                                                                          |
| ---------------------------------------------------------- | --------------------------: | ------------------------------------------------------------------------------------------------- |
| Harness sanity: every expected proof still verifies        |                     52 / 52 | `benchmark_manifest.json` plus fixture `expected_proof.lean` checks                               |
| Package setup works through Pi                             |           1 / 1 smoke proof | `results/20260506T_pi_package_setup_action_smoke`                                                 |
| Post-registry package setup works through Pi               |           1 / 1 smoke proof | `results/20260506T_pi_package_registry_setup_smoke`                                               |
| Package fixture groups work through Pi                     |           1 / 1 smoke proof | `results/20260506T_pi_package_fixture_group_smoke`                                                |
| Combined broader + held-out transfer stability             |      42 / 42 fixture-trials | `results/20260506T_combined_broader_heldout_pre_repair_hint_variance`                             |
| Post-registry package combined run                         |              14 / 14 proved | `results/20260506T_pi_package_registry_combined_seeded`                                           |
| Synthetic hints are rejected on expanded negative controls | 45 / 45 candidates rejected | `results/20260506T_expanded_negative_control_probe`                                               |
| Post-registry package negative-control rejection           | 15 / 15 candidates rejected | `results/20260506T_pi_package_registry_negative_controls_attempts3`                               |
| Negative controls recover with larger fallback budget      |              6 / 6 fixtures | `results/20260506T_expanded_negative_controls_pre_repair_hint_no_pregenerate_attempts3_timeout60` |
| Post-registry package negative-control recovery            |              6 / 6 fixtures | `results/20260506T_pi_package_registry_negative_controls_attempts3`                               |
| Package dry-run excludes result artifacts and tests        |  runtime package files only | `npm pack --dry-run --json`                                                                       |

## Runtime dependency contract

This package is a Pi wrapper around an autocontext Lean verification harness. The TypeScript extension imports Pi runtime modules from `@earendil-works/*`; the proof-repair harness invokes autocontext as an on-demand Python CLI runtime:

```text
uvx --python 3.12 --from autocontext==0.4.8 autoctx improve ...
```

Preflight checks both `uvx` and `autocontext==0.4.8` / `autoctx improve` availability. This keeps autocontext as the real repair-engine dependency while Lean remains the proof oracle.

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

## Interpretation

- `combined` validates transfer stability across broader and held-out fixtures.
- `negative_controls` validates safety: generated candidates are useful only when Lean accepts them; rejected candidates are discarded and Pi repair remains the fallback.
- Current evidence supports an experimental package, not a general theorem prover claim.
