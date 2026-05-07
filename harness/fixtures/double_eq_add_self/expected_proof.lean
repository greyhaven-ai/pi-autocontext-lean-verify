induction n with
| zero => rfl
| succ n ih =>
    rw [doubleAdd, ih]
    simp [Nat.succ_eq_add_one, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
