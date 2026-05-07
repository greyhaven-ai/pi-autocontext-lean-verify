induction a with
| zero => rfl
| succ a ih =>
    simp [mulSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
