induction n with
| zero => rfl
| succ n ih =>
    rw [triple, ih, Nat.mul_succ]
