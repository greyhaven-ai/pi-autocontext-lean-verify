set_option linter.unusedSimpArgs false

/-- Recursor adding three with a constant offset. -/
def triOffset : Nat -> Nat
| 0 => 5
| n + 1 => triOffset n + 3

/-- Normalization-playbook benchmark: shifted recursive triples equal `n + n + n + 5`. -/
theorem triOffset_eq_self_sum_add_five (n : Nat) : triOffset n = n + n + n + 5 := by
{{PROOF}}
