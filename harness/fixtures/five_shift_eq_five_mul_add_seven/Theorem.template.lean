set_option linter.unusedSimpArgs false

/-- Recursive function incrementing by five from offset seven. -/
def fiveShift : Nat -> Nat
| 0 => 7
| n + 1 => fiveShift n + 5

/-- Expanded mixed benchmark: shifted recursive fives equal `5 * n + 7`. -/
theorem fiveShift_eq_five_mul_add_seven (n : Nat) : fiveShift n = 5 * n + 7 := by
{{PROOF}}
