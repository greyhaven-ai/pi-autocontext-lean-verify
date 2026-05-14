# Dedicated Repository Split

`pi-autocontext-lean-verify` is ready to leave the autocontext worktree as a dedicated experimental Pi package repository.

GitHub repo:

```text
https://github.com/greyhaven-ai/pi-autocontext-lean-verify.git
```

Local staged repo:

```text
/Users/jayscambler/Repositories/pi-autocontext-lean-verify
```

## Target layout

```text
pi-autocontext-lean-verify/
  package.json
  extensions/
  skills/
  prompts/
  docs/
  fixture_groups.json
  harness/
    benchmark_manifest.json
    fixtures/
    playbooks/expanded_mixed_cluster_v1.md
    run_playbook_transfer.py
    prove_with_autocontext.py
    experiment_common.py
    verify_lean_proof.py
    extract_candidate_proof.py
    update_results_index.py
  tests/
    package_validation.py
```

## Split decisions

- Keep the formal-proof work as a Pi package, not autocontext core.
- Bundle the minimal harness runtime under `harness/` so the package can preflight and run without `AUTOCONTEXT_FORMAL_ROOT`.
- Keep `AUTOCONTEXT_FORMAL_ROOT` as an override for local experiments.
- Use `pi-autocontext-lean-verify` as the repo and npm package name.
- Import Pi runtime modules from `@earendil-works/*`.
- Keep autocontext as an explicit runtime dependency via `uvx --python 3.12 --from autocontext==0.5.1 autoctx improve`.
- Keep `private: true` until license and release policy are finalized.
- Exclude `harness/results/` from git and npm packaging.

## Local staged validation

The staged repo passed:

```text
python3 tests/package_validation.py                         # OK, 7 tests
npm pack --dry-run --json                                  # includes harness, excludes results/tests
pi -e . action=preflight                                   # harness root = packageRoot/harness
pi -e . action=setup runRoot=results/20260506T_standalone_earendil_setup_smoke
```

Standalone setup result:

```text
1 / 1 proved
Pi calls: 0
Lean verifier attempts: 1
```

## Remaining before first npm publication

- Choose license.
- Decide whether the Lean harness Python runtime should remain bundled or be split into a separate harness package later.
- Add CI for `python3 tests/package_validation.py`, `npm pack --dry-run --json`, and expected-proof Lean verification.
- Keep public claims scoped to verifier-backed proof repair experiments, not general theorem proving.
