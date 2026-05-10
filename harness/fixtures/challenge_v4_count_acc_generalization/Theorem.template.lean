set_option linter.unusedSimpArgs false

/-- Count occurrences of a target Nat in a list, using local recursion. -/
def countSlow (target : Nat) : List Nat -> Nat
| [] => 0
| x :: xs => (if x = target then 1 else 0) + countSlow target xs

/-- Tail-recursive occurrence counter with an accumulator. -/
def countAcc (target : Nat) : List Nat -> Nat -> Nat
| [], acc => acc
| x :: xs, acc => countAcc target xs ((if x = target then 1 else 0) + acc)

/-- Challenge v4: accumulator generalization for a conditional list counter. -/
theorem countAcc_eq_countSlow_add (target : Nat) (xs : List Nat) (acc : Nat) :
    countAcc target xs acc = countSlow target xs + acc := by
{{PROOF}}
