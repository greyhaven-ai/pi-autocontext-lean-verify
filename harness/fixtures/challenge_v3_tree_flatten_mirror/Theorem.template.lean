set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse implemented with the local slow append. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

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

/-- Challenge v3: flattening a mirrored tree is the slow reverse of the original flattening.
    A robust proof generally needs generalized append/reverse helper lemmas. -/
theorem flatten_mirror_eq_revSlow_flatten (tree : NatTree) :
    flatten (mirror tree) = revSlow (flatten tree) := by
{{PROOF}}
