set_option linter.unusedSimpArgs false

/-- Recursive function incrementing by six from offset one. -/
def sixShift : Nat -> Nat
| 0 => 1
| n + 1 => sixShift n + 6

/-- Held-out transfer benchmark: shifted recursive sixes equal `6 * n + 1`. -/
theorem sixShift_eq_six_mul_add_one (n : Nat) : sixShift n = 6 * n + 1 := by
{{PROOF}}
