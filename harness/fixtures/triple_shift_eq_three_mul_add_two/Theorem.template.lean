set_option linter.unusedSimpArgs false

/-- Recursive triple with a constant offset. -/
def tripleShift : Nat -> Nat
| 0 => 2
| n + 1 => tripleShift n + 3

/-- Arithmetic-recursion benchmark: shifted recursive triples equal `3 * n + 2`. -/
theorem tripleShift_eq_three_mul_add_two (n : Nat) : tripleShift n = 3 * n + 2 := by
{{PROOF}}
