/-- A custom recursive identity-like Nat function. -/
def countUp : Nat -> Nat
| 0 => 0
| n + 1 => countUp n + 1

/-- Hidden-proof benchmark: the recursive counter returns its input. -/
theorem countUp_eq_self (n : Nat) : countUp n = n := by
{{PROOF}}
