induction n with
| zero => rfl
| succ n ih =>
    simp [fiveShift, ih, Nat.mul_add, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
