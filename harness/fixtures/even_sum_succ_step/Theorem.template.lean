set_option linter.unusedSimpArgs false

/-- Recursive function adding successive even numbers. -/
def evenSum : Nat -> Nat
| 0 => 0
| n + 1 => evenSum n + 2 * (n + 1)

/-- Arithmetic-recursion benchmark: normalize the successor step of evenSum. -/
theorem evenSum_succ_step (n : Nat) : evenSum (n + 1) = evenSum n + 2 * n + 2 := by
{{PROOF}}
