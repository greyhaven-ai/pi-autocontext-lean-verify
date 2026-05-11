---
name: lean-verify
summary: Verifier-backed Lean proof repair using autocontext and Pi.
description: Use when running the experimental Lean formal-proof harness, validating machine-checked proof candidates, benchmarking playbook transfer, or invoking the pi-autocontext-lean-verify package. Triggers: Lean proof repair, formal proof, theorem proving, verifier-backed proof, autocontext formal, proof playbook, pre-repair hints.
---

# Formal Proof Harness

Use this skill for the external Lean proof-repair experiment harness. The package wraps `support/formal-proof-lean-pilot` and exposes the `autocontext_lean_verify` Pi tool.

## Core rule

Lean is the correctness oracle. Never count prose, mathematical-looking text, or an LLM's claim of success as a theorem proof. A proof succeeds only when the fixed Lean theorem template compiles with the candidate proof body.

## Guardrails

The harness rejects or avoids:

- `sorry`
- `admit`
- new axioms
- `unsafe`
- theorem weakening
- changing theorem statements
- new imports / proof-by-importing-answer
- candidates that are not proof bodies for the `{{PROOF}}` placeholder

## Recommended workflow

Benchmark and attribution actions default to short temp result paths under `the system temp directory (`pi-autocontext-lean-verify/...`)` (or `$AUTOCONTEXT_LEAN_VERIFY_RESULTS_ROOT`) so npm-loaded packages avoid Pi session path-length failures.

Use `challenge_v6_frontier` and `challenge_v7_frontier` for packaged verifier-only frontier suites. v7 is the first packaged suite where seeded autocontext is intentionally unstable while unseeded/direct solve none. Use source-only `challenge_v8_diagnostics` to isolate the partition-heavy accumulator frontier into smaller components.


1. Run setup or preflight first:

```json
{
  "action": "setup"
}
```

or:

```json
{
  "action": "preflight"
}
```

`setup` runs preflight and a minimal Lean smoke proof.

2. For the current strongest repair-only mode, use a named fixture group:

```json
{
  "action": "run",
  "mode": "pre_repair_hint",
  "fixtureGroup": "broader"
}
```

This maps to the validated harness flags:

```text
--no-pregenerate
--structured-alternate-retry
--structured-hint-candidates
--pre-repair-hint-candidates
--max-attempts 2
--rounds 2
--timeout 60
```

3. For expanded negative controls, prefer `maxAttempts=3`:

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

4. To reproduce the proof-transfer benchmark, compare seeded autocontext/Pi against direct Pi repair-loop on no-expected-proof challenge fixtures:

```json
{
  "action": "benchmark",
  "fixtureGroup": "challenge_v3_generalization",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

This mode uses `--no-pregenerate` and `--structured-alternate-retry`; synthetic hint candidates are disabled.

5. For seeded/unseeded/direct attribution on v5 fixtures:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v5_attribution",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

6. Summarize a run with:

```json
{
  "action": "summarize",
  "runRoot": "results/<run>"
}
```

## Fixture groups

- `smoke`: one quick theorem, `add_zero_right`.
- `broader`: seven broader fixtures covering Nat distribution, Bool/List recursion, list helpers, tree helpers, and reverse/append.
- `heldout`: seven original held-out transfer fixtures.
- `combined`: `broader` + `heldout` (`14` fixtures).
- `negative_controls`: six fixtures where generic Nat/List hint candidates should fail Lean before fallback: distribution, multiplication associativity/commutativity, addition cancellation, and filter length bound.
- `challenge_v2_no_helper`: three no-expected-proof fixtures requiring local helper lemma discovery.
- `challenge_v3_generalization`: four no-expected-proof theorem-generalization fixtures requiring accumulator and multi-helper proof plans.
- `challenge_transfer`: all v2/v3 challenge fixtures (`7` fixtures).
- `challenge_v4_count`: four no-expected-proof count/list/tree fixtures.
- `challenge_v5_attribution`: four no-expected-proof simultaneous-invariant and multi-helper composition fixtures.
- `challenge_v5_tree_tally`: one hard tree/tally mirror fixture.
- `challenge_v6_frontier`: four frontier fixtures covering multi-accumulator reverse invariants, nested tree partition stats, successor-map reverse count/sum, and mutual tree stats.
- `challenge_v7_frontier`: four frontier-plus fixtures combining partition/tree mirror composition with stats accumulator normalization.
- `challenge_v8_diagnostics`: four source-only diagnostic fixtures isolating the v7 partition-heavy accumulator frontier into smaller components.
- `challenge_extended_transfer`: all v2/v3/v4/v5/v6/v7/v8 challenge fixtures (`27` fixtures).

## Modes

- `seeded_pregenerate`: allow Pi/autocontext to pregenerate from the verified playbook, then Lean-check.
- `pre_repair_hint`: no pregeneration; try Lean-checked strategy candidates before primary Pi repair.
- `post_repair_hint`: no pregeneration; run primary Pi repair, then Lean-checked hints before alternate Pi fallback.
- `structured_retry`: no pregeneration; structured alternate Pi retry without hint candidates.

## Interpretation guidance

- Challenge fixtures intentionally omit `expected_proof.lean`; success must come from the generated proof body passing Lean.
- Use `action="attribution"` when comparing seeded, unseeded isolated, and direct Pi repair-loop outcomes.
- Treat `pre_repair_hint` as a hybrid experiment mode, not pure LLM proof generation.
- Lean-rejected hint candidates are good safety evidence when fallback recovers.
- Compare methods using proof success, Pi calls, Lean verifier attempts, repair edits, and token edit distance.
- Keep artifacts indexed with `results/index.json` and `results/EXPERIMENTS.md`.

## Packaging status

This package is npm-distributed as `pi-autocontext-lean-verify`. Current patch releases use GitHub trusted publishing with npm provenance. The package remains experimental: report proof-transfer results as verifier-backed evidence, not as a claim that autocontext is a standalone theorem prover.
