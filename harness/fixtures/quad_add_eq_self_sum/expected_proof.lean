induction n with
| zero => rfl
| succ n ih =>
    rw [quadAdd, ih]
    omega
