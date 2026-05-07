# Verifier-backed Lean proof repair

Use the `autocontext_lean_verify` tool to run or summarize the external Lean proof-repair harness.

Principles:

- Lean is the correctness oracle.
- Do not count a proof unless Lean verifies it against the unchanged theorem template.
- Prefer `action=setup` or `action=preflight` before long runs.
- Prefer `mode=pre_repair_hint` for the current strongest repair-only mode.
- Prefer named fixture groups (`smoke`, `broader`, `heldout`, `combined`, `negative_controls`) over manually listing fixtures unless the user requests a custom subset.
- Preserve durable artifacts under `results/` and update the index after each run.

Suggested first call:

```json
{
  "action": "setup"
}
```

Suggested broader smoke run:

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

Suggested negative-control recovery run:

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

When reporting results, include:

- Lean-verified proofs / total
- failed fixtures
- Pi calls
- Lean verifier attempts
- pre-repair hint generated/passed/used
- primary repair and alternate fallback counts
- result artifact paths
