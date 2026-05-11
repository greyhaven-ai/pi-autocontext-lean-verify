set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse implemented with local slow append. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Slow length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => Nat.succ (lengthSlow xs)

/-- Slow sum over Nat lists. -/
def sumSlow : List Nat -> Nat
| [] => 0
| x :: xs => x + sumSlow xs

/-- Count occurrences of a target Nat in a list, using local recursion. -/
def countSlow (target : Nat) : List Nat -> Nat
| [] => 0
| x :: xs => (if x = target then 1 else 0) + countSlow target xs

/-- Slow successor map over Nat lists. -/
def mapSuccSlow : List Nat -> List Nat
| [] => []
| x :: xs => Nat.succ x :: mapSuccSlow xs

/-- Challenge v6: successor-map after reverse shifts count targets and adds one per element to sums. -/
theorem mapSucc_revSlow_count_sum (target : Nat) (xs : List Nat) :
    countSlow (Nat.succ target) (mapSuccSlow (revSlow xs)) = countSlow target xs ∧
      sumSlow (mapSuccSlow (revSlow xs)) = sumSlow xs + lengthSlow xs := by
{{PROOF}}
