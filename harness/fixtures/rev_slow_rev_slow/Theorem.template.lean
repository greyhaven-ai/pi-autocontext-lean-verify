set_option linter.unusedSimpArgs false

/-- Slow reverse over Nat lists. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => revSlow xs ++ [x]

/-- Harder benchmark: reversing with the custom reverse twice is identity. -/
theorem revSlow_revSlow (xs : List Nat) : revSlow (revSlow xs) = xs := by
{{PROOF}}
