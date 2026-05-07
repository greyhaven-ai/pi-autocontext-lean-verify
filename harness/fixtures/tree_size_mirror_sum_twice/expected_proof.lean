induction tree with
| leaf => rfl
| node left value right ihLeft ihRight =>
    simp [mirror, treeSize, ihLeft, ihRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
    omega
