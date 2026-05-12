# V15 Proof-Shape Hint Fixtures

`challenge_v15_proof_shape_hints` is a source follow-up to the v13/v14 order-sensitivity frontier. V14 plus focused repeats showed that the full simultaneous keep/drop length/count/sum theorem remains stochastic even with a larger per-call timeout. V15 asks whether the missing ingredient is final proof structure rather than low-level theorem truth: each fixture exposes harmless theorem hypotheses that name the metric bundles, side bundles, append/filter helper lemmas, or final reassembly shape.

Lean remains the only correctness oracle. These fixtures intentionally do **not** bundle `expected_proof.lean`; local witness proofs were used only to validate theorem truth and initial `rfl` failure.

## Fixtures

| Fixture | Diagnostic hint supplied |
| --- | --- |
| `challenge_v15_order_length_count_sum_from_metric_hyps` | Metric-grouped length/count/sum hypotheses; proof only reassembles groups in the hard length/count/sum order. |
| `challenge_v15_order_length_count_sum_from_side_hyps` | Side-grouped keep/drop hypotheses; proof reassembles side bundles into length/count/sum metric groups. |
| `challenge_v15_order_length_count_sum_with_append_hyps` | Append metric lemmas plus keep/drop append lemmas supplied; proof still performs tree induction through mirror/flatten. |
| `challenge_v15_order_length_count_sum_with_append_and_reassembly_hyp` | Append/filter helper lemmas plus an explicit final reassembly hypothesis; proof can focus on deriving six scalar equalities before calling the reassembler. |

## Local verification

Each fixture has a local-only witness proof under `/tmp/v15_*.proof.lean` and was checked with `harness/verify_lean_proof.py`. For all four fixtures:

- local witness proof: Lean verified;
- initial proof `rfl`: Lean rejected;
- bundled `expected_proof.lean`: absent.

## Suggested attribution command

```bash
npm run benchmark:v15
```

Equivalent Pi tool input:

```json
{
  "action": "attribution",
  "fixtureGroup": "challenge_v15_proof_shape_hints",
  "maxAttempts": 2,
  "rounds": 2,
  "timeoutSeconds": 120
}
```

Use the same controlled comparison interpretation as v8-v14: Pi provider only, no pregeneration, synthetic hints disabled, structured alternate retry, and Lean verification as the only success oracle.

## Controlled attribution result

Run root:
`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260512T195739Z_attribution_benchmark_challenge_v15_proof_shape_hints`

Settings: Pi provider, v6 seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

| Method | Result | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 3 / 4 | 5 | 361.32s | 11 |
| unseeded isolated autocontext | 0 / 4 | 8 | 7.22s | 8 |
| direct Pi repair-loop | 2 / 4 | 4 | 283.21s | n/a |

| Fixture | Seeded | Unseeded | Direct |
| --- | ---: | ---: | ---: |
| `challenge_v15_order_length_count_sum_from_metric_hyps` | proved | failed | proved |
| `challenge_v15_order_length_count_sum_from_side_hyps` | proved | failed | proved |
| `challenge_v15_order_length_count_sum_with_append_hyps` | proved | failed | failed |
| `challenge_v15_order_length_count_sum_with_append_and_reassembly_hyp` | failed | failed | failed |

Interpretation: v15 separates final reassembly from tree-induction proof synthesis. Metric-group and side-group reassembly are easy enough that direct Pi solves them, while unseeded autocontext still fails under the isolated repair loop. Supplying append/filter helper lemmas lets seeded autocontext solve the hard length/count/sum tree-mirror theorem at timeout 120; direct and unseeded still fail it. Adding an explicit final reassembly hypothesis did **not** help in this run and likely increased prompt/type complexity: the only seeded miss was `with_append_and_reassembly_hyp`, whose primary repair returned no extracted proof. The frontier therefore is not final conjunction assembly alone; it is the interaction of recognizing the induction/simp proof shape with the available helper hypotheses under a small Pi repair budget.
