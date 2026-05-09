set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse implemented with the local slow append. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Sum a Nat list with local recursion. -/
def sumSlow : List Nat -> Nat
| [] => 0
| x :: xs => x + sumSlow xs

/-- Challenge v2: prove slow reverse preserves sum without a predeclared append-sum helper. -/
theorem sumSlow_revSlow_noHelper (xs : List Nat) : sumSlow (revSlow xs) = sumSlow xs := by
{{PROOF}}
