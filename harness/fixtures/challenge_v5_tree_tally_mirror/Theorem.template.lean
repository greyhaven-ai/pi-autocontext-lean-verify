set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => Nat.succ (lengthSlow xs)

/-- Count occurrences of a target Nat in a list, using local recursion. -/
def countSlow (target : Nat) : List Nat -> Nat
| [] => 0
| x :: xs => (if x = target then 1 else 0) + countSlow target xs

/-- Tail-recursive tally carrying both occurrence count and total length accumulators. -/
def tallyAcc (target : Nat) : List Nat -> Nat -> Nat -> Nat × Nat
| [], hits, total => (hits, total)
| x :: xs, hits, total =>
    tallyAcc target xs ((if x = target then 1 else 0) + hits) (Nat.succ total)

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

/-- Challenge v5: mirrored flattening preserves the simultaneous tally accumulator. -/
theorem tallyAcc_flatten_mirror
    (target : Nat) (tree : NatTree) (hits total : Nat) :
    tallyAcc target (flatten (mirror tree)) hits total =
      tallyAcc target (flatten tree) hits total := by
{{PROOF}}
