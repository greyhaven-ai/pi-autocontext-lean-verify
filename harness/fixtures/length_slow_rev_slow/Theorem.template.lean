set_option linter.unusedSimpArgs false

/-- Slow list length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => lengthSlow xs + 1

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Helper available in the fixed template: slow append length is additive. -/
theorem lengthSlow_appendSlow_helper (xs ys : List Nat) : lengthSlow (appendSlow xs ys) = lengthSlow xs + lengthSlow ys := by
  induction xs with
  | nil => simp [appendSlow, lengthSlow]
  | cons x xs ih =>
      simp [appendSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

/-- Slow reverse over Nat lists. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Held-out transfer benchmark: slow reverse preserves slow length using the helper lemma. -/
theorem lengthSlow_revSlow (xs : List Nat) : lengthSlow (revSlow xs) = lengthSlow xs := by
{{PROOF}}
