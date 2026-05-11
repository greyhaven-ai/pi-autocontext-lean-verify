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

-- Mutually recursive even/odd depth value lists.
mutual
  def evenValues : NatTree -> List Nat
  | leaf => []
  | node left value right => value :: appendSlow (oddValues left) (oddValues right)

  def oddValues : NatTree -> List Nat
  | leaf => []
  | node left _ right => appendSlow (evenValues left) (evenValues right)
end

/-- Challenge v7: mutually recursive depth-value traversals lifted through stats accumulators under mirror. -/
theorem depthValuesStatsAcc_mirror
    (target : Nat) (tree : NatTree)
    (hitsE totalE sumE hitsO totalO sumO : Nat) :
    statsAcc target (evenValues (mirror tree)) hitsE totalE sumE =
        statsAcc target (evenValues tree) hitsE totalE sumE ∧
      statsAcc target (oddValues (mirror tree)) hitsO totalO sumO =
        statsAcc target (oddValues tree) hitsO totalO sumO := by
{{PROOF}}
