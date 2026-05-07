induction xs with
| nil => rfl
| cons x xs ih =>
    simp [ih]
