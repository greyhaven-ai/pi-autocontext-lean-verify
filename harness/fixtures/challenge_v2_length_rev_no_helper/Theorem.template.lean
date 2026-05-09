set_option linter.unusedSimpArgs false

/-- Slow list length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => lengthSlow xs + 1

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse over Nat lists. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Challenge v2: prove slow reverse preserves slow length without a predeclared append-length helper. -/
theorem lengthSlow_revSlow_noHelper (xs : List Nat) : lengthSlow (revSlow xs) = lengthSlow xs := by
{{PROOF}}
