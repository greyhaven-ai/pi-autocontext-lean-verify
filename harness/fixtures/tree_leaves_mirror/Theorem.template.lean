set_option linter.unusedSimpArgs false

/-- Binary tree carrying Nat values. -/
inductive NatTree where
| leaf : NatTree
| node : NatTree -> Nat -> NatTree -> NatTree

open NatTree

/-- Mirror a tree. -/
def mirror : NatTree -> NatTree
| leaf => leaf
| node left value right => node (mirror right) value (mirror left)

/-- Count leaves in a tree. -/
def leaves : NatTree -> Nat
| leaf => 1
| node left _ right => leaves left + leaves right

/-- Mirroring preserves leaf count. -/
theorem leavesMirror (tree : NatTree) : leaves (mirror tree) = leaves tree := by
{{PROOF}}
