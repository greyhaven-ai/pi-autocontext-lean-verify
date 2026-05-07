induction n with
| zero => rfl
| succ n ih =>
    simp [repeatTrue, andAll, ih]
