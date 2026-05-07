set_option linter.unusedSimpArgs false

/-- Slow multiplication by recursion on the first argument. -/
def mulSlow : Nat -> Nat -> Nat
| 0, _ => 0
| n + 1, m => mulSlow n m + m

/-- Harder benchmark: custom multiplication distributes over right-side addition. -/
theorem mulSlow_add_right (a b c : Nat) : mulSlow a (b + c) = mulSlow a b + mulSlow a c := by
{{PROOF}}
