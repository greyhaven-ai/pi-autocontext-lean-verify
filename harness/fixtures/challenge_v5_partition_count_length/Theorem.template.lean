set_option linter.unusedSimpArgs false

/-- Slow length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => Nat.succ (lengthSlow xs)

/-- Count occurrences of a target Nat in a list, using local recursion. -/
def countSlow (target : Nat) : List Nat -> Nat
| [] => 0
| x :: xs => (if x = target then 1 else 0) + countSlow target xs

/-- Keep elements equal to the target. -/
def keepEqSlow (target : Nat) : List Nat -> List Nat
| [] => []
| x :: xs => if x = target then x :: keepEqSlow target xs else keepEqSlow target xs

/-- Keep elements not equal to the target. -/
def dropEqSlow (target : Nat) : List Nat -> List Nat
| [] => []
| x :: xs => if x = target then dropEqSlow target xs else x :: dropEqSlow target xs

/-- Challenge v5: simultaneous partition/count/length invariant. -/
theorem keep_drop_count_length_invariant (target : Nat) (xs : List Nat) :
    lengthSlow (keepEqSlow target xs) = countSlow target xs ∧
      lengthSlow (dropEqSlow target xs) + countSlow target xs = lengthSlow xs := by
{{PROOF}}
