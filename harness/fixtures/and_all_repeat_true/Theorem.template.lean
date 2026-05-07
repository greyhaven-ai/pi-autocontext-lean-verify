/-- Repeat true n times. -/
def repeatTrue : Nat -> List Bool
| 0 => []
| n + 1 => true :: repeatTrue n

/-- Boolean conjunction over a Bool list. -/
def andAll : List Bool -> Bool
| [] => true
| x :: xs => x && andAll xs

/-- Non-arithmetic recursive Bool/List fixture. -/
theorem andAllRepeatTrue (n : Nat) : andAll (repeatTrue n) = true := by
{{PROOF}}
