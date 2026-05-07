set_option linter.unusedSimpArgs false

/-- Recursor adding three, with a reassociated statement. -/
def triAlt : Nat -> Nat
| 0 => 0
| n + 1 => triAlt n + 3

/-- Normalization-playbook benchmark: recursive triples equal `(n + n) + n`. -/
theorem triAlt_eq_reassociated (n : Nat) : triAlt n = (n + n) + n := by
{{PROOF}}
