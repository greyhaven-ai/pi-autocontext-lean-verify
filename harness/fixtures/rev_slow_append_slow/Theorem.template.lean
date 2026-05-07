set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse implemented with the local slow append. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Associativity of the local slow append. -/
theorem appendSlowAssoc (xs ys zs : List Nat) :
    appendSlow (appendSlow xs ys) zs = appendSlow xs (appendSlow ys zs) := by
  induction xs with
  | nil =>
      simp [appendSlow]
  | cons x xs ih =>
      simp [appendSlow, ih]

/-- Right identity for the local slow append. -/
theorem appendSlowNilRight (xs : List Nat) : appendSlow xs [] = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp [appendSlow, ih]

/-- Reversing a slow append swaps the reversed parts. -/
theorem revSlowAppendSlow (xs ys : List Nat) :
    revSlow (appendSlow xs ys) = appendSlow (revSlow ys) (revSlow xs) := by
{{PROOF}}
