set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse implemented with the local slow append. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Tail-recursive reverse with an accumulator. -/
def revAcc : List Nat -> List Nat -> List Nat
| [], acc => acc
| x :: xs, acc => revAcc xs (x :: acc)

/-- Challenge v3: prove accumulator reverse matches slow reverse at the empty accumulator.
    The direct statement is intentionally too weak for structural induction; a stronger
    accumulator-generalized helper is usually needed. -/
theorem revAcc_empty_eq_revSlow (xs : List Nat) : revAcc xs [] = revSlow xs := by
{{PROOF}}
