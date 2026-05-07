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

4. Summarize a run with:

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

## Modes

- `seeded_pregenerate`: allow Pi/autocontext to pregenerate from the verified playbook, then Lean-check.
- `pre_repair_hint`: no pregeneration; try Lean-checked strategy candidates before primary Pi repair.
- `post_repair_hint`: no pregeneration; run primary Pi repair, then Lean-checked hints before alternate Pi fallback.
- `structured_retry`: no pregeneration; structured alternate Pi retry without hint candidates.

## Interpretation guidance

- Treat `pre_repair_hint` as a hybrid experiment mode, not pure LLM proof generation.
- Lean-rejected hint candidates are good safety evidence when fallback recovers.
- Compare methods using proof success, Pi calls, Lean verifier attempts, repair edits, and token edit distance.
- Keep artifacts indexed with `results/index.json` and `results/EXPERIMENTS.md`.

## Packaging status

This package is experimental and local-first. It is intended to become its own npm-distributed Pi package after broader validation and negative controls. Linear tracking issue: `AC-731`.
