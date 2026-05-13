# V16 compact reassembly hint diagnostics

`challenge_v16_compact_reassembly_hints` is a post-`0.1.12` diagnostic suite that keeps the hard v15 length/count/sum simultaneous keep/drop theorem shape but replaces the large tree-specific higher-order reassembly hypothesis with compact generic or named first-order packer hypotheses.

## Fixture design

All four fixtures intentionally ship without `expected_proof.lean`; local witness proofs are used only to prove theorem truth and are not bundled.

| Fixture | Compact hint shape | Intent |
| --- | --- | --- |
| `challenge_v16_order_length_count_sum_with_top_level_packer` | generic `∀ P Q R : Prop, P → Q → R → P ∧ Q ∧ R` | Add only a small top-level metric-pair packer. |
| `challenge_v16_order_length_count_sum_with_pair_and_top_packers` | generic pair packer plus generic top-level packer | Add compact Prop-level pair and metric-bundle assembly hints. |
| `challenge_v16_order_length_count_sum_with_nat_scalar_packer` | generic first-order Nat scalar packer | Replace tree-specific reassembly with a reusable scalar equality packer. |
| `challenge_v16_order_length_count_sum_with_named_metric_packers` | named length/count/sum pair packers plus top-level packer | Split reassembly into compact metric-local named helpers. |

## Local verification

Local-only witness proofs verify all four fixtures, and `rfl` is rejected for all four initial proofs.

| Check | Result |
| --- | ---: |
| Local witness proofs | 4 / 4 |
| Initial `rfl` rejected | 4 / 4 |
| Bundled expected proofs | 0 |

## Controlled attribution

Run root:

`/var/folders/5l/4d99c0cd27183q3rdnm8ybg00000gn/T/pi-autocontext-lean-verify/20260512T210612Z_attribution_benchmark_challenge_v16_compact_reassembly_hints`

Settings: Pi provider, v6 seed playbook, `--no-pregenerate`, synthetic hints disabled, `--structured-alternate-retry`, `--max-attempts 2`, `--rounds 2`, `--timeout 120`.

| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts |
| --- | ---: | ---: | ---: | ---: |
| seeded autocontext | 2 / 4 | 6 | 290.80s | 10 |
| unseeded isolated autocontext | 0 / 4 | 8 | 7.56s | 8 |
| direct Pi repair-loop | 0 / 4 | 4 | 467.40s | n/a |

| Fixture | Seeded | Unseeded isolated | Direct repair-loop |
| --- | ---: | ---: | ---: |
| top-level Prop packer | proved | failed | failed |
| pair + top-level Prop packers | failed | failed | failed |
| generic Nat scalar packer | proved | failed | failed |
| named metric packers | failed | failed | failed |

The two seeded successes used the packer hypotheses directly (`exact packMetricPairs` / `exact packMetricScalars`) with the familiar induction/simp arithmetic proof shape. The two seeded misses returned the unchanged `rfl` proof in the full-suite run.

## Focused seeded repeat probes

Because prior frontier misses have often been stochastic, the two first-run misses were repeated three times each in seeded-only mode with the same controlled repair settings.

Run root:

`/tmp/pi-v16-focused-miss-stability-20260512T212001Z`

| Fixture | Repeat 1 | Repeat 2 | Repeat 3 | Focused aggregate | Including original v16 attribution |
| --- | ---: | ---: | ---: | ---: | ---: |
| pair + top-level Prop packers | proved | failed | proved | 2 / 3 | 2 / 4 |
| named metric packers | proved | failed | proved | 2 / 3 | 2 / 4 |

Per-repeat costs:

| Run | Result | Final attempt | Pi calls | Pi elapsed | Lean attempts | Features |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| pair + top repeat 1 | proved | 1 | 1 | 205.20s | 3 | induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |
| pair + top repeat 2 | failed | — | 2 | 263.49s | 2 | rfl |
| pair + top repeat 3 | proved | 1 | 1 | 103.69s | 3 | induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |
| named metric repeat 1 | proved | 1 | 1 | 171.52s | 3 | induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |
| named metric repeat 2 | failed | — | 2 | 260.90s | 2 | rfl |
| named metric repeat 3 | proved | 1 | 1 | 169.53s | 3 | induction, simp, exact, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |

## Timeout-240 focused repeat probe

The same two first-run misses were also repeated three times each with the same seeded-only settings except `--timeout 240`.

Run root:

`/tmp/pi-v16-timeout240-focused-stability-20260512T214817Z`

| Fixture | Repeat 1 | Repeat 2 | Repeat 3 | Timeout-240 aggregate |
| --- | ---: | ---: | ---: | ---: |
| pair + top-level Prop packers | proved | proved | failed | 2 / 3 |
| named metric packers | proved | proved | proved | 3 / 3 |

Per-repeat costs:

| Run | Result | Final attempt | Pi calls | Pi elapsed | Lean attempts | Features |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| pair + top timeout-240 repeat 1 | proved | 1 | 1 | 182.95s | 3 | induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |
| pair + top timeout-240 repeat 2 | proved | 1 | 1 | 173.05s | 3 | induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |
| pair + top timeout-240 repeat 3 | failed | — | 2 | 7064.45s | 2 | rfl |
| named metric timeout-240 repeat 1 | proved | 1 | 2 | 2972.73s | 2 | induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |
| named metric timeout-240 repeat 2 | proved | 1 | 1 | 128.00s | 3 | induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |
| named metric timeout-240 repeat 3 | proved | 1 | 1 | 165.98s | 3 | induction, simp, exact, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm |

Important caveat: timeout 240 improved the named-metric focused aggregate but did **not** stabilize pair+top. It also exposed severe wall-clock blowups. In the pair+top failed repeat, both primary and alternate repairs reported `pi CLI timed out after 240s`, but the recorded process elapsed times were 1869.95s and 5194.50s. In the named-metric first repeat, the primary repair reported the same Pi timeout but consumed 2756.93s before the alternate repair succeeded in 215.80s. Timeout 240 is therefore not a clean practical stabilization knob for v16.

## Interpretation

V16 sharpens the v15 prompt-shape result. Compact generic hints are not a full stabilization fix, but they are less harmful than the large v15 tree-specific `mkMetrics` hypothesis:

- top-level Prop packing and generic Nat scalar packing solved in the first controlled seeded run;
- the two first-run compact-packer misses were stochastic, solving `2/3` on focused repeat (`2/4` including the original miss for each);
- timeout 240 improved the named-metric focused repeat to `3/3`, but pair+top remained `2/3` and the run showed pathological wall-clock blowups despite Pi timeout messages;
- unseeded isolated autocontext and direct Pi repair-loop solved none of the four v16 tree-induction fixtures.

Compared with v15, final conjunction assembly remains secondary: the real frontier is recognizing the tree-induction/simp arithmetic proof shape under compact-but-extra helper hypotheses. The v15 large higher-order reassembly hypothesis was `1/4` including its original run; v16 compact variants recover more often but still show stochastic timeout/empty-repair behavior under the two-attempt, 120s baseline. Timeout 240 is evidence of recoverability, not a release-quality stabilization strategy.
