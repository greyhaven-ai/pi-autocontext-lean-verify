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

/-- Challenge v4: reversing a list preserves the custom occurrence count. -/
theorem countSlow_revSlow (target : Nat) (xs : List Nat) :
    countSlow target (revSlow xs) = countSlow target xs := by
{{PROOF}}
