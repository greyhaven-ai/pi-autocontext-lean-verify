set_option linter.unusedSimpArgs false

/-- Small binary tree for induction benchmark. -/
inductive NatTree where
| leaf : NatTree
| node : NatTree -> Nat -> NatTree -> NatTree

/-- Mirror a NatTree by swapping left and right recursively. -/
def mirror : NatTree -> NatTree
| NatTree.leaf => NatTree.leaf
| NatTree.node left value right => NatTree.node (mirror right) value (mirror left)

/-- Harder benchmark: mirroring twice returns the original tree. -/
theorem mirror_mirror (tree : NatTree) : mirror (mirror tree) = tree := by
{{PROOF}}
