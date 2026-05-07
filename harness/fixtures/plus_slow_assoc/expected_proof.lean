induction a with
| zero =>
    induction b with
    | zero => rfl
    | succ b ih => simp [plusSlow, ih]
| succ a ih =>
    simp [plusSlow, ih]
