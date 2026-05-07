induction n with
| zero => rfl
| succ n ih =>
    rw [quadSlow, ih, Nat.mul_succ]
