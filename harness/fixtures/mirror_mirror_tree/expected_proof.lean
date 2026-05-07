induction tree with
| leaf => rfl
| node left value right left_ih right_ih =>
    simp [mirror, left_ih, right_ih]
