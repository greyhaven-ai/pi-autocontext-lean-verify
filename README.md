# pi-autocontext-lean-verify

Experimental Pi package for verifier-backed Lean proof repair using autocontext and Pi.

Working product framing:

> A Pi plugin for verifier-backed formal proof repair using autocontext and Lean.

This is **not** a general theorem prover and should not be described as “autocontext proves theorems.” Pi/autocontext proposes and repairs proof bodies; Lean is the correctness oracle.

## Status

- Experimental npm package: `pi-autocontext-lean-verify@0.1.0`.
- Tracks Linear issue `AC-731`.
- License: Apache-2.0.
- Default harness root in the standalone package: bundled `harness/` directory.
- `AUTOCONTEXT_FORMAL_ROOT` can override the harness root for local experiments.

## Install

From npm:

```bash
pi install pi-autocontext-lean-verify
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

## Provided resources

- Extension tool: `autocontext_lean_verify`
- Skill: `lean-verify`
- Prompt template: `lean-verify.md`
- Fixture group registry: `fixture_groups.json`
- Domain model, validation matrix, and repo split notes: `docs/DOMAIN.md`, `docs/VALIDATION.md`, `docs/REPO_SPLIT.md`

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
Fixture count: 52
Fixture groups: smoke=1, broader=7, heldout=7, combined=14, negative_controls=6
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

`npm pack --dry-run --json` includes runtime package assets and the bundled harness, while excluding tests and generated result artifacts.

## Release

Version `0.1.0` is the initial experimental npm release. Future releases should use GitHub's npm trusted publisher workflow:

```text
.github/workflows/publish.yml
environment: publish-pi-autocontext-lean-verify
npm publish --provenance --access public
```

Before cutting the next release:

- keep CI green,
- bump `package.json` version,
- tag/release `v<version>` in GitHub,
- let the trusted publisher workflow publish to npm.
