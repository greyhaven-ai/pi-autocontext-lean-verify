induction xs with
| nil =>
    simp [appendSlow, revSlow, appendSlowNilRight]
| cons x xs ih =>
    simp [appendSlow, revSlow, ih, appendSlowAssoc]
