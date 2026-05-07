set_option linter.unusedSimpArgs false

/-- Recursor equivalent to adding three copies of the input. -/
def tripleAdd : Nat -> Nat
| 0 => 0
| n + 1 => tripleAdd n + 3

/-- Arithmetic-recursion benchmark: recursive triples equal `n + n + n`. -/
theorem tripleAdd_eq_self_sum (n : Nat) : tripleAdd n = n + n + n := by
{{PROOF}}
