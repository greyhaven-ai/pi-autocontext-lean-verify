set_option linter.unusedSimpArgs false

/-- A custom recursive function that increments by two. -/
def doubleAdd : Nat -> Nat
| 0 => 0
| n + 1 => doubleAdd n + 2

/-- Hidden-proof benchmark: recursive doubles equal adding the input to itself. -/
theorem double_eq_add_self (n : Nat) : doubleAdd n = n + n := by
{{PROOF}}
