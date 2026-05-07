induction xs with
| nil =>
    simp [appendSlow, sumSlow]
| cons x xs ih =>
    simp [appendSlow, sumSlow, ih, Nat.add_assoc]
