/-- Filtering a list cannot increase its length; generic list induction hints alone are insufficient. -/
theorem filterLengthLeBuiltin (p : Nat -> Bool) (xs : List Nat) : (List.filter p xs).length <= xs.length := by
{{PROOF}}
