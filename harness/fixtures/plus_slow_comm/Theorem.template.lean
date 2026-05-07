set_option linter.unusedSimpArgs false

/-- Custom addition by recursion on the first argument. -/
def plusSlow : Nat -> Nat -> Nat
| 0, m => m
| n + 1, m => Nat.succ (plusSlow n m)

/-- Harder benchmark: prove commutativity for custom recursive addition. -/
theorem plusSlow_comm (a b : Nat) : plusSlow a b = plusSlow b a := by
{{PROOF}}
