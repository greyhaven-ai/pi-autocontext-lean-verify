set_option linter.unusedSimpArgs false

/-- Slow multiplication by recursion on the first argument. -/
def mulSlow : Nat -> Nat -> Nat
| 0, _ => 0
| n + 1, m => mulSlow n m + m

/-- Expanded mixed benchmark: incrementing the right factor adds the left factor. -/
theorem mulSlow_succ_right (a b : Nat) : mulSlow a (b + 1) = mulSlow a b + a := by
{{PROOF}}
