induction n with
| zero => rfl
| succ n ih =>
    simp [pentaAdd, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
