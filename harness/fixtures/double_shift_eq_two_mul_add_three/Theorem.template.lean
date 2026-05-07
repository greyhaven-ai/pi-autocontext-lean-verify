set_option linter.unusedSimpArgs false

/-- Recursive double with a constant offset. -/
def doubleShift : Nat -> Nat
| 0 => 3
| n + 1 => doubleShift n + 2

/-- Arithmetic-recursion benchmark: shifted recursive doubles equal `2 * n + 3`. -/
theorem doubleShift_eq_two_mul_add_three (n : Nat) : doubleShift n = 2 * n + 3 := by
{{PROOF}}
