induction n with
| zero => rfl
| succ n ih =>
    rw [countUp, ih]
