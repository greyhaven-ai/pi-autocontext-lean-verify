set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse implemented with the local slow append. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Double every element using local recursion. -/
def mapDoubleSlow : List Nat -> List Nat
| [] => []
| x :: xs => (x + x) :: mapDoubleSlow xs

/-- Challenge v3: mapping double over a reversed append should split into reversed mapped parts.
    The proof usually needs both a map-append helper and a reverse-append helper. -/
theorem mapDoubleSlow_revSlow_appendSlow (xs ys : List Nat) :
    mapDoubleSlow (revSlow (appendSlow xs ys)) =
      appendSlow (mapDoubleSlow (revSlow ys)) (mapDoubleSlow (revSlow xs)) := by
{{PROOF}}
