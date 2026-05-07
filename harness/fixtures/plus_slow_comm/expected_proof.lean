have plus_zero : ∀ n : Nat, plusSlow n 0 = n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
      simp [plusSlow, ih]
have plus_succ : ∀ n m : Nat, plusSlow n (Nat.succ m) = Nat.succ (plusSlow n m) := by
  intro n m
  induction n with
  | zero => rfl
  | succ n ih =>
      simp [plusSlow, ih]
induction a with
| zero =>
    simp [plusSlow, plus_zero]
| succ a ih =>
    rw [plusSlow, ih, plus_succ]
