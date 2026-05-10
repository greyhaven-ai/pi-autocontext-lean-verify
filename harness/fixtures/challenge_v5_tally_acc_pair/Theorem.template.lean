set_option linter.unusedSimpArgs false

/-- Count occurrences of a target Nat in a list, using local recursion. -/
def countSlow (target : Nat) : List Nat -> Nat
| [] => 0
| x :: xs => (if x = target then 1 else 0) + countSlow target xs

/-- Slow length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => Nat.succ (lengthSlow xs)

/-- Tail-recursive tally carrying both occurrence count and total length accumulators. -/
def tallyAcc (target : Nat) : List Nat -> Nat -> Nat -> Nat × Nat
| [], hits, total => (hits, total)
| x :: xs, hits, total =>
    tallyAcc target xs ((if x = target then 1 else 0) + hits) (Nat.succ total)

/-- Challenge v5: simultaneous accumulator generalization for count and length. -/
theorem tallyAcc_eq_countSlow_lengthSlow
    (target : Nat) (xs : List Nat) (hits total : Nat) :
    tallyAcc target xs hits total =
      (countSlow target xs + hits, lengthSlow xs + total) := by
{{PROOF}}
