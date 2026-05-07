induction xs with
| nil => rfl
| cons x xs ih =>
    simp [revSlow, lengthSlow_appendSlow_helper, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
