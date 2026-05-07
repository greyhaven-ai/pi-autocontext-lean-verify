induction a with
| zero => simp [mulSlow]
| succ a ih =>
    rw [Nat.succ_add]
    simp [mulSlow, ih, Nat.add_assoc]
    rw [Nat.add_comm]
