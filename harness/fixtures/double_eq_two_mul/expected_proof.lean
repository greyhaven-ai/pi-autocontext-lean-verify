  induction n with
  | zero => rfl
  | succ n ih =>
      simp [double, ih, Nat.mul_succ, Nat.add_comm]
