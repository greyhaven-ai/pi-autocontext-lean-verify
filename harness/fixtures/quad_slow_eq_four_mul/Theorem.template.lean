set_option linter.unusedSimpArgs false

/-- Recursive function incrementing by four. -/
def quadSlow : Nat -> Nat
| 0 => 0
| n + 1 => quadSlow n + 4

/-- Arithmetic-recursion benchmark: recursive quads equal multiplication by four. -/
theorem quadSlow_eq_four_mul (n : Nat) : quadSlow n = 4 * n := by
{{PROOF}}
