induction tree with
| leaf => rfl
| node left value right left_ih right_ih =>
    simp [mirror, treeSize, left_ih, right_ih]
    omega
