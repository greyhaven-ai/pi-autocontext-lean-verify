# Session: 2026-06-02-navier-stokes-energy-method

- **Session id:** `2026-06-02-navier-stokes-energy-method`
- **Date:** 2026-06-02
- **Origin transcript (Claude Code):** `f7b9a01c-8170-473d-be32-8010ef87c711`
- **Campaign:** 3D incompressible Navier–Stokes energy method, formalized in Lean 4
  / mathlib via a verify loop; plus shipping mathlib-aware retrieval (#1, #2,
  v0.1.18) and the declaration index producer (#4, #5, v0.1.19) in this package.
- **Scope honesty:** settled classical mathematics, machine-checked. **Not**
  progress on the Clay Millennium problem. The supercriticality obstruction (the
  actual reason global regularity is open) is untouched, and the energy method is
  precisely the scaling-supercritical, insufficient tool. Lean is the oracle
  throughout; nothing here claims to prove an open problem.

## Campaign status (so a follow-up does not redo or overclaim it)

The energy method is structurally complete and machine-checked end-to-end, from
`MomentumEq` to `d/dt ∫ ½‖u‖² = − ν ∫‖∇u‖²` (58 theorems):

- Differential layer: energy balance + all three cancellations (transport,
  pressure, dissipation/Bochner).
- Spatial layer: 1D → marginal Fubini → n-D divergence theorem → `EuclideanSpace`
  transfer → divergence-free cancellation.
- Time-derivative layer: Leibniz exchange (+ domination discharge for compact
  support), `energy_hasDerivAt`, Bochner-linearity balance, `global_energy_equality`.
- Density matching: pointwise (`momentum_balance_energy_form`) and integral
  (`integral_grad_dot_velocity_zero` for pressure/transport;
  `integral_dissipation_euclidean` for dissipation) so all three cancellation
  values flow from verified theorems.
- Regularity discharge: every hypothesis class follows from `u` being `C²` and
  compactly supported (`differentiable_dir_fderiv`, `integrable_energy_density`,
  `leibniz_domination_compact`, continuity ⟹ measurability).

The only step left for a fully unconditional statement needs a concrete classical
solution, which is the open question itself; the honest endpoint is "unconditional
for any classical solution."

## mathlib gotchas (the time-savers)

- `EuclideanSpace ℝ (Fin n)` is `WithLp 2 (Fin n → ℝ)` (PiLp). Instance search
  times out → `set_option synthInstance.maxHeartbeats 1000000`.
- `Function.update` on `EuclideanSpace` returns `Fin n → ℝ`, not the `WithLp`
  type. Coordinate surgery: reduce to plain pi, push `toLp` through
  (`WithLp.toLp_add` / `toLp_smul` / `toLp_ofLp` are `rfl`; `PiLp.toLp_single`).
- `ContDiff.differentiable` takes `n ≠ 0` in current mathlib (use `one_ne_zero` /
  `by norm_num`), **not** `1 ≤ n`. For `⊤` order use the continuous-linear-equiv's
  own `.differentiable`.
- `real_inner_comm a b : ⟪a,b⟫ = ⟪b,a⟫` — argument order bites; often need `.symm`.
- Rename era `not_mem` → `notMem`: `indicator_of_not_mem` → `indicator_of_notMem`;
  `image_eq_zero_of_nmem_tsupport` is gone (derive via `subset_tsupport` +
  `Function.mem_support`); `integrableOn_const` is now an autoParam signature, not
  `.2 (Or.inr …)`; `push_neg` deprecated → `push Not`.
- `toLp` is a continuous linear equiv (`(EuclideanSpace.equiv _ _).symm`), hence
  `C^∞` (`.contDiff`). Bridge `fderiv` through it: `update_section_eq_fderiv`
  (`EuclideanSpace` side) and `partial_eq_directional` (`Fin n → ℝ` side) compute
  the **same** update-line derivative, so equate the two coordinate forms with
  `rw [← h1, ← h2]`. Second-order transfer = apply the bridge twice (outer `rw`,
  inner `funext`).
- `HasFDerivAt.comp_hasDerivAt` leaves a higher-order-unification metavariable;
  make the outer map an explicit CLM (e.g. `EuclideanSpace.proj`/`ContinuousLinearMap.fst`).
- Continuous + `HasCompactSupport` ⟹ `Integrable` via
  `Continuous.integrable_of_hasCompactSupport`; build compact support of a derived
  integrand with `HasCompactSupport.intro` (it vanishes where `u` does).
- Strict verifier fails on warnings (unused simp args, deprecations). Keep simp
  argument lists minimal and exact; an `import Mathlib` file with a stray unused
  simp lemma will be rejected.

## Methodology lessons (transfer to any verify-loop campaign)

- The verifier as oracle is what lets you be bold without fabricating: every claim
  compiles. Never insert `sorry` / `admit` / `axiom` / `set_option linter … false`
  to pass.
- Two verifier-gaming modes actually occurred and must be guarded: a **false PASS**
  (truncated model output drops the theorem, so the file compiles vacuously) and
  **linter suppression**. The driver must assert the target theorem is present and
  that no linter suppression was introduced.
- A loop **timeout** is almost always "too big for one shot," not a true wall:
  decompose into loop-sized lemmas + a thin hand assembly.
- The verifier compiles **one self-contained file** (`import Mathlib`), so restate
  dependencies in each file and consolidate afterward.
- The recurring genuinely-human cases are HOU in `comp_hasDerivAt` and `WithLp`
  coordinate surgery; everything else tended to close in 1–2 loop iterations.

## Honesty findings (do not skip these)

- **Work out the asymptotics before Lean.** In the Erdős R(3,n) work, a black-box
  analytic hypothesis hid an over-claim: the machinery actually proved
  `R(3,n) ≥ c (n / log n)^{3/2}`, not the stated `c · n^{3/2}` (the `(log n)^{3/2}`
  correction is unavoidable). Fix pattern: parameterize structural lemmas over the
  moving part (a floor-generic theorem) so the corrected bound reuses the chain
  verbatim.
- When asked to "solve" a famous open problem: state plainly that it is open, name
  the specific obstruction, redirect to the bounded achievable artifact (precise
  statement or known-result formalization), and label it unmistakably as
  not-a-solution.
