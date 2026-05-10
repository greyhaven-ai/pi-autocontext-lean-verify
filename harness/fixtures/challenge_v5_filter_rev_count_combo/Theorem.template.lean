set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse implemented with local slow append. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Count occurrences of a target Nat in a list, using local recursion. -/
def countSlow (target : Nat) : List Nat -> Nat
| [] => 0
| x :: xs => (if x = target then 1 else 0) + countSlow target xs

/-- Keep elements equal to the target. -/
def keepEqSlow (target : Nat) : List Nat -> List Nat
| [] => []
| x :: xs => if x = target then x :: keepEqSlow target xs else keepEqSlow target xs

/-- Challenge v5: reverse commutes with the custom filter and the filter preserves target count. -/
theorem keepEqSlow_revSlow_and_count (target : Nat) (xs : List Nat) :
    keepEqSlow target (revSlow xs) = revSlow (keepEqSlow target xs) ∧
      countSlow target (keepEqSlow target xs) = countSlow target xs := by
{{PROOF}}
