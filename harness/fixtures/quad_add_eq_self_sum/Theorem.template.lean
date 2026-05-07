set_option linter.unusedSimpArgs false

/-- Recursor equivalent to adding four copies of the input. -/
def quadAdd : Nat -> Nat
| 0 => 0
| n + 1 => quadAdd n + 4

/-- Arithmetic-recursion benchmark: recursive quads equal `n + n + n + n`. -/
theorem quadAdd_eq_self_sum (n : Nat) : quadAdd n = n + n + n + n := by
{{PROOF}}
