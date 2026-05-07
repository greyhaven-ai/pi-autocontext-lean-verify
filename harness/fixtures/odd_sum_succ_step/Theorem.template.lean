set_option linter.unusedSimpArgs false

/-- Recursive function adding successive odd numbers. -/
def oddSum : Nat -> Nat
| 0 => 0
| n + 1 => oddSum n + (2 * n + 1)

/-- Arithmetic-recursion benchmark: normalize the successor step of oddSum. -/
theorem oddSum_succ_step (n : Nat) : oddSum (n + 1) = oddSum n + 2 * n + 1 := by
{{PROOF}}
