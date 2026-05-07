set_option linter.unusedSimpArgs false

/-- Slow list length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => lengthSlow xs + 1

/-- Slow map that increments every Nat. -/
def mapSuccSlow : List Nat -> List Nat
| [] => []
| x :: xs => (x + 1) :: mapSuccSlow xs

/-- Held-out transfer benchmark: slow successor-map preserves slow length. -/
theorem lengthSlow_mapSuccSlow (xs : List Nat) : lengthSlow (mapSuccSlow xs) = lengthSlow xs := by
{{PROOF}}
