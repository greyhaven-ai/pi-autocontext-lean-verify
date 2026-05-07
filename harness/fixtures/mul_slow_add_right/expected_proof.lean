induction a with
| zero => rfl
| succ a ih =>
    rw [mulSlow, mulSlow, mulSlow, ih]
    omega
