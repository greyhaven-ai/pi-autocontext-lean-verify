induction n with
| zero => rfl
| succ n ih =>
    simp [triAlt, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
