set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow reverse implemented with the local slow append. -/
def revSlow : List Nat -> List Nat
| [] => []
| x :: xs => appendSlow (revSlow xs) [x]

/-- Map successor over Nat lists using local recursion. -/
def mapSuccSlow : List Nat -> List Nat
| [] => []
| x :: xs => (x + 1) :: mapSuccSlow xs

/-- Challenge v2: prove slow reverse commutes with successor-map without a predeclared map-append helper. -/
theorem mapSuccSlow_revSlow_noHelper (xs : List Nat) :
    mapSuccSlow (revSlow xs) = revSlow (mapSuccSlow xs) := by
{{PROOF}}
