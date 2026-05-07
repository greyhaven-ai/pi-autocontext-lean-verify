set_option linter.unusedSimpArgs false

/-- Slow multiplication by recursion on the first argument. -/
def mulSlow : Nat -> Nat -> Nat
| 0, _ => 0
| a + 1, b => mulSlow a b + b

/-- Held-out transfer benchmark: slow multiplication distributes over left addition. -/
theorem mulSlow_add_left (a b c : Nat) : mulSlow (a + b) c = mulSlow a c + mulSlow b c := by
{{PROOF}}
