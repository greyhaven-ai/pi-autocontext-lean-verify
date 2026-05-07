induction n with
| zero => rfl
| succ n ih =>
    rw [doubleShift, ih, Nat.mul_succ]
