induction xs with
| nil =>
    simp [appendSlow, mapDoubleSlow]
| cons x xs ih =>
    simp [appendSlow, mapDoubleSlow, ih]
