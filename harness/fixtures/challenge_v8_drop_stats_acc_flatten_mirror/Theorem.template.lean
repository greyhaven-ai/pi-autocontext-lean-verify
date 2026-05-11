set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

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

/-- Keep elements equal to the target. -/
def keepEqSlow (target : Nat) : List Nat -> List Nat
| [] => []
| x :: xs => if x = target then x :: keepEqSlow target xs else keepEqSlow target xs

/-- Drop elements equal to the target. -/
def dropEqSlow (target : Nat) : List Nat -> List Nat
| [] => []
| x :: xs => if x = target then dropEqSlow target xs else x :: dropEqSlow target xs

/-- Tail-recursive stats carrying occurrence count, total length, and sum accumulators. -/
def statsAcc (target : Nat) : List Nat -> Nat -> Nat -> Nat -> Nat × Nat × Nat
| [], hits, total, sum => (hits, total, sum)
| x :: xs, hits, total, sum =>
    statsAcc target xs ((if x = target then 1 else 0) + hits) (Nat.succ total) (x + sum)

/-- Binary tree carrying Nat values. -/
inductive NatTree where
| leaf : NatTree
| node : NatTree -> Nat -> NatTree -> NatTree

open NatTree

/-- Mirror a tree. -/
def mirror : NatTree -> NatTree
| leaf => leaf
| node left value right => node (mirror right) value (mirror left)

/-- In-order flattening of a tree. -/
def flatten : NatTree -> List Nat
| leaf => []
| node left value right => appendSlow (flatten left) (value :: flatten right)

/-- Challenge v8 diagnostic: drop-side partition stats through tree mirror, isolated from keep-side conjunctions. -/
theorem dropStatsAcc_flatten_mirror
    (target : Nat) (tree : NatTree) (hits total sum : Nat) :
    statsAcc target (dropEqSlow target (flatten (mirror tree))) hits total sum =
      statsAcc target (dropEqSlow target (flatten tree)) hits total sum := by
{{PROOF}}
