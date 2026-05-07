/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Double each element of a Nat list. -/
def mapDoubleSlow : List Nat -> List Nat
| [] => []
| x :: xs => (x + x) :: mapDoubleSlow xs

/-- Slow map distributes over the local slow append. -/
theorem mapDoubleSlowAppendSlow (xs ys : List Nat) :
    mapDoubleSlow (appendSlow xs ys) = appendSlow (mapDoubleSlow xs) (mapDoubleSlow ys) := by
{{PROOF}}
