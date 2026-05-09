set_option linter.unusedSimpArgs false

/-- Sum a Nat list with local recursion. -/
def sumSlow : List Nat -> Nat
| [] => 0
| x :: xs => x + sumSlow xs

/-- Tail-recursive sum with an accumulator. -/
def sumAcc : List Nat -> Nat -> Nat
| [], acc => acc
| x :: xs, acc => sumAcc xs (acc + x)

/-- Challenge v3: prove accumulator sum matches structural sum at zero.
    The proof usually needs a stronger theorem generalized over the accumulator. -/
theorem sumAcc_zero_eq_sumSlow (xs : List Nat) : sumAcc xs 0 = sumSlow xs := by
{{PROOF}}
