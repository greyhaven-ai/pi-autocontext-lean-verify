induction xs with
| nil => rfl
| cons x xs ih => simp [mapSuccSlow, lengthSlow, ih]
