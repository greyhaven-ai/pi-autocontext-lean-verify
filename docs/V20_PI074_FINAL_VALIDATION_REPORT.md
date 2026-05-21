# V20 Pi 0.74 / Lean 4.27 final validation report

This report records the post-release Pi-only validation evidence gathered after:

- publishing upstream timeout cleanup in `autocontext==0.5.1` / `autoctx@0.5.1`;
- publishing `pi-autocontext@0.2.5` under the `@earendil-works/*` Pi package scope;
- validating `pi-autocontext-lean-verify@0.1.17` against the updated runtime stack; and
- aligning the local Pi CLI to `0.74.0`.

Lean remains the correctness oracle. A run counts only when the proof body produced for `{{PROOF}}` verifies against the unchanged Lean theorem template.

## Guardrails

All counted results used the same proof-safety guardrails:

- Pi provider only;
- unchanged theorem templates;
- candidate supplies only the `{{PROOF}}` body;
- no `sorry`, `admit`, theorem weakening, new axioms, `unsafe`, proof-by-importing-answer, or `set_option autoImplicit true`;
- Lean binary `/tmp/autocontext-elan-home/bin/lean`;
- Lean `4.27.0` after toolchain repair;
- `autocontext==0.5.1` via `uvx`;
- baseline `maxAttempts=2`;
- baseline timeout `120s`;
- `240s` probes are recovery evidence only, not clean stabilization evidence.

## Environment for the final clean V20 run

```text
variant=v20-watchdog-extension
seed_playbook=harness/playbooks/challenge_v20_description_only_skeleton_v1.md
pi_binary=/opt/homebrew/bin/pi
pi_version=0.74.0
lean_binary=/tmp/autocontext-elan-home/bin/lean
elan_home=/tmp/autocontext-elan-home
Lean (version 4.27.0, arm64-apple-darwin24.6.0, commit db93fe1608548721853390a10cd40580fe7d22ae, Release)
autocontext_package_version=0.5.1
provider=pi
timeout=120
max_attempts=2
rounds=2
per_repeat_watchdog_seconds=900
```

Final clean V20 root:

```text
/tmp/pi074-lean427-v20-watchdog-extension-20260521T151757Z
```

Final 240s recovery root:

```text
/tmp/pi074-lean427-v20-watchdog-extension-20260521T151757Z/recovery_timeout240_timeout_misses
```

## V18 / V20 / V23 aligned-stack comparison

Before the longer V20 follow-up, the aligned stack was compared across three seed shapes on the same two clean compact-packer fixtures:

- `challenge_v18_pair_top_packers_clean`
- `challenge_v18_named_metric_packers_clean`

Settings: Pi CLI `0.74.0`, Lean `4.27.0`, `autocontext==0.5.1`, `maxAttempts=2`, `rounds=2`, `timeout=120`, `--no-pregenerate`, `--structured-alternate-retry`.

| Variant | Seed playbook | Overall | Full 2/2 repeats | Pair fixture | Named fixture | Failure modes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| V18 | `harness/playbooks/challenge_v18_prompt_only_skeleton_v1.md` | 15 / 20 | 6 / 10 | 8 / 10 | 7 / 10 | 3 timeout/no-candidate; 2 malformed/extracted-candidate plus timeout elsewhere |
| V20 | `harness/playbooks/challenge_v20_description_only_skeleton_v1.md` | 17 / 20 | 8 / 10 | 8 / 10 | 9 / 10 | 3 timeout/no-candidate |
| V23 | `harness/playbooks/challenge_v23_exact_labels_without_plan_prefix_v1.md` | 14 / 20 | 5 / 10 | 7 / 10 | 7 / 10 | 6 timeout/no-candidate |

All counted successes in this comparison were directly rechecked with Lean, and forbidden construct scans found 0 violations.

Interpretation: V20 was the strongest observed seed shape in the aligned 10-repeat comparison, but the margin over V18 was small enough to require a longer follow-up.

## Lean toolchain contamination incident

A later watchdog extension temporarily produced a misleading `0 / 20` V20 result. That root is excluded from the final evidence:

```text
/tmp/pi074-lean427-v20-watchdog-extension-20260520T163912Z
```

Diagnostic root before repair:

```text
/tmp/pi074-lean427-current-degradation-diagnostics-20260521T042055Z
```

The failure was contaminated by a broken Lean toolchain state. Direct Lean execution failed with:

```text
missing data file for module Init.Guard
```

After reinstalling `leanprover/lean4:v4.27.0` under `/tmp/autocontext-elan-home`, both direct Lean and Pi/Lean diagnostics recovered.

Post-repair diagnostic root:

```text
/tmp/pi074-lean427-current-degradation-diagnostics-post-leanfix-20260521T044520Z
```

Post-repair diagnostics:

| Diagnostic | Result |
| --- | ---: |
| Easy `mul_add_distrib_right` at 120s | 1 / 1 |
| V20 single repeat at 240s | 2 / 2 |

The contaminated `0 / 20` watchdog root is therefore excluded from all final stability/capability conclusions.

## Clean post-fix V20 20-repeat baseline

Run root:

```text
/tmp/pi074-lean427-v20-watchdog-extension-20260521T151757Z
```

| Scope | Fixture successes | Success rate | Full 2/2 repeats |
| --- | ---: | ---: | ---: |
| Clean post-fix V20 20 repeats | 28 / 40 | 70% | 11 / 20 |
| Original valid V20 10 repeats | 17 / 20 | 85% | 8 / 10 |
| Combined non-contaminated, temporally separated | 45 / 60 | 75% | 19 / 30 |

The combined row is useful context, but it is temporally separated evidence rather than a single controlled 30-repeat run.

### By fixture

| Fixture | Clean post-fix result |
| --- | ---: |
| `challenge_v18_pair_top_packers_clean` | 15 / 20 |
| `challenge_v18_named_metric_packers_clean` | 13 / 20 |

### 120s failure modes

| Mode | Count |
| --- | ---: |
| `no_candidate_primary_or_alternate_timeout` | 12 |

All clean post-fix 120s failures were timeout/no-candidate misses. No counted failure was a Lean-accepted invalid proof.

## 240s recovery of post-fix 120s misses

Recovery root:

```text
/tmp/pi074-lean427-v20-watchdog-extension-20260521T151757Z/recovery_timeout240_timeout_misses
```

| Recovery set | Result |
| --- | ---: |
| Timeout-only misses from clean post-fix V20 20-repeat baseline | 12 / 12 |

Recovery evidence is diagnostic only. It does **not** change the `120s` baseline result or denominator.

## Final guardrail checks

| Check | Result |
| --- | ---: |
| 120s successful candidates directly rechecked with Lean | 28 / 28 |
| 240s recovery candidates directly rechecked with Lean | 12 / 12 |
| Forbidden construct/option violations across baseline + recovery candidates | 0 |

## Interpretation

V20 description-only remains the strongest current seed shape in the post-Pi-0.74 validation set, but it is not clean-stable at the controlled `120s` baseline:

- clean post-fix V20: `28 / 40` fixture successes;
- clean post-fix full-repeat stability: `11 / 20` repeats solved both fixtures;
- combined non-contaminated V20 evidence: `45 / 60` fixture successes;
- all clean post-fix baseline failures were timeout/no-candidate misses;
- every clean post-fix timeout miss recovered at `240s`.

The main conclusion is therefore:

> V20 is capable and comparatively strongest among V18/V20/V23, but current Pi-provider runs are `120s`-budget-limited. It should be described as capable with strong recovery at `240s`, not clean-stable at `120s`.

## Operational recommendations

1. Keep `maxAttempts=2` and `timeout=120` as the controlled baseline for comparability.
2. Treat `timeout=240` as recovery/capability evidence unless a new baseline is explicitly declared.
3. Before long Lean/Pi runs, preflight both:
   - `ELAN_HOME=/tmp/autocontext-elan-home /tmp/autocontext-elan-home/bin/lean --version`
   - a direct Lean smoke such as `#eval 1`.
4. Quarantine any run where Lean fails with toolchain-level errors such as `missing data file for module Init.Guard`.
5. If product operation requires reliability rather than strict baseline comparability, evaluate an explicit intermediate timeout policy such as `180s` against V20.
6. If prompt-shape research continues, run attribution controls for V20 under the repaired toolchain before proposing a V26 variant.
