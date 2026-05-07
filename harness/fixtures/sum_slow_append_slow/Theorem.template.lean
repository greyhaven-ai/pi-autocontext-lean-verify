set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Sum a Nat list. -/
def sumSlow : List Nat -> Nat
| [] => 0
| x :: xs => x + sumSlow xs

/-- Sum distributes over the local slow append. -/
theorem sumSlowAppendSlow (xs ys : List Nat) :
    sumSlow (appendSlow xs ys) = sumSlow xs + sumSlow ys := by
{{PROOF}}
