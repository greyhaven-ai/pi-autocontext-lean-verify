set_option linter.unusedSimpArgs false

/-- Recursor adding four, stated as a sum of two pairs. -/
def quadPair : Nat -> Nat
| 0 => 0
| n + 1 => quadPair n + 4

/-- Normalization-playbook benchmark: recursive quads equal `(n + n) + (n + n)`. -/
theorem quadPair_eq_pair_sum (n : Nat) : quadPair n = (n + n) + (n + n) := by
{{PROOF}}
