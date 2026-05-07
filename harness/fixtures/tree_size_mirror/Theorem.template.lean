set_option linter.unusedSimpArgs false

/-- Small binary tree for induction benchmark. -/
inductive NatTree where
| leaf : NatTree
| node : NatTree -> Nat -> NatTree -> NatTree

/-- Mirror a NatTree by swapping left and right recursively. -/
def mirror : NatTree -> NatTree
| NatTree.leaf => NatTree.leaf
| NatTree.node left value right => NatTree.node (mirror right) value (mirror left)

/-- Count nodes in a NatTree. -/
def treeSize : NatTree -> Nat
| NatTree.leaf => 0
| NatTree.node left _ right => treeSize left + treeSize right + 1

/-- Harder benchmark: mirroring preserves tree size. -/
theorem treeSize_mirror (tree : NatTree) : treeSize (mirror tree) = treeSize tree := by
{{PROOF}}
