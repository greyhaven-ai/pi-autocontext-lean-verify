induction n with
| zero => rfl
| succ n ih =>
    rw [tripleAdd, ih]
    omega
