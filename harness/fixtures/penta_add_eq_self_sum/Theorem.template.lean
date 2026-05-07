set_option linter.unusedSimpArgs false

/-- Recursor adding five, requiring a longer additive normalization. -/
def pentaAdd : Nat -> Nat
| 0 => 0
| n + 1 => pentaAdd n + 5

/-- Normalization-playbook benchmark: recursive pentuples equal five copies of `n`. -/
theorem pentaAdd_eq_self_sum (n : Nat) : pentaAdd n = n + n + n + n + n := by
{{PROOF}}
