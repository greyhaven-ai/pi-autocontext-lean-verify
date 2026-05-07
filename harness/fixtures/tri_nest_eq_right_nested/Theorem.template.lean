set_option linter.unusedSimpArgs false

/-- Recursor adding three, with a theorem using right-nested self-addition. -/
def triNest : Nat -> Nat
| 0 => 0
| n + 1 => triNest n + 3

/-- Normalization-playbook benchmark: recursive triples equal `n + (n + n)`. -/
theorem triNest_eq_right_nested (n : Nat) : triNest n = n + (n + n) := by
{{PROOF}}
