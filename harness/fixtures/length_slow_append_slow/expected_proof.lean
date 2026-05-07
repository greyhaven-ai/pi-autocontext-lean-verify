induction xs with
| nil => simp [appendSlow, lengthSlow]
| cons x xs ih =>
    simp [appendSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
