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

-- Mutually recursive even/odd depth statistics: occurrence count and value sum.
mutual
  def evenDepthStats (target : Nat) : NatTree -> Nat × Nat
  | leaf => (0, 0)
  | node left value right =>
      ((if value = target then 1 else 0) + (oddDepthStats target left).1 + (oddDepthStats target right).1,
        value + (oddDepthStats target left).2 + (oddDepthStats target right).2)

  def oddDepthStats (target : Nat) : NatTree -> Nat × Nat
  | leaf => (0, 0)
  | node left _ right =>
      ((evenDepthStats target left).1 + (evenDepthStats target right).1,
        (evenDepthStats target left).2 + (evenDepthStats target right).2)
end

/-- Challenge v6: mirror preservation for mutually recursive even/odd depth statistics. -/
theorem depthStats_mirror (target : Nat) (tree : NatTree) :
    evenDepthStats target (mirror tree) = evenDepthStats target tree ∧
      oddDepthStats target (mirror tree) = oddDepthStats target tree := by
{{PROOF}}
