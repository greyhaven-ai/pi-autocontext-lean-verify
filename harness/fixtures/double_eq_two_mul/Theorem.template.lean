set_option linter.unusedSimpArgs false

/-- A deliberately small hidden-proof calibration function. -/
def double : Nat -> Nat
| 0 => 0
| n + 1 => double n + 2

/-- Calibration theorem: the recursively defined `double` equals multiplication by two. -/
theorem double_eq_two_mul (n : Nat) : double n = 2 * n := by
{{PROOF}}
