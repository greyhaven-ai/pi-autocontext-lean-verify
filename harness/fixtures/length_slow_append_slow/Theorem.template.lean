set_option linter.unusedSimpArgs false

/-- Slow list length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => lengthSlow xs + 1

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Expanded mixed benchmark: length of slow append is additive. -/
theorem lengthSlow_appendSlow (xs ys : List Nat) : lengthSlow (appendSlow xs ys) = lengthSlow xs + lengthSlow ys := by
{{PROOF}}
