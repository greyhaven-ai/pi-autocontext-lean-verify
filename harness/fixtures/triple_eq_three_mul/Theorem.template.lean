set_option linter.unusedSimpArgs false

/-- A custom recursive function that increments by three. -/
def triple : Nat -> Nat
| 0 => 0
| n + 1 => triple n + 3

/-- Hidden-proof benchmark: recursive triples equal multiplication by three. -/
theorem triple_eq_three_mul (n : Nat) : triple n = 3 * n := by
{{PROOF}}
