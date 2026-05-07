have rev_append : ∀ xs ys : List Nat, revSlow (xs ++ ys) = revSlow ys ++ revSlow xs := by
  intro xs ys
  induction xs with
  | nil =>
      simp [revSlow]
  | cons x xs ih =>
      simp [revSlow, ih, List.append_assoc]
induction xs with
| nil => rfl
| cons x xs ih =>
    simp [revSlow, rev_append, ih]
