induction n with
| zero => rfl
| succ n ih =>
    rw [tripleShift, ih, Nat.mul_succ]
