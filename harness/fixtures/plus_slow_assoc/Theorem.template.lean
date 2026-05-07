set_option linter.unusedSimpArgs false

/-- Slow addition by recursion on the first argument. -/
def plusSlow : Nat -> Nat -> Nat
| 0, b => b
| a + 1, b => plusSlow a b + 1

/-- Held-out transfer benchmark: associativity for a custom recursive addition. -/
theorem plusSlow_assoc (a b c : Nat) : plusSlow (plusSlow a b) c = plusSlow a (plusSlow b c) := by
{{PROOF}}
