set_option linter.unusedSimpArgs false

/-- Recursive function adding seven copies of n by successor. -/
def sevenAdd : Nat -> Nat
| 0 => 0
| n + 1 => sevenAdd n + 7

/-- Held-out transfer benchmark: sevenAdd unfolds to seven explicit copies of n. -/
theorem sevenAdd_eq_self_sum (n : Nat) : sevenAdd n = n + n + n + n + n + n + n := by
{{PROOF}}
