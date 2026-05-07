/-- Multiplication associativity should use the library theorem, not generic additive induction hints. -/
theorem mulAssocBuiltin (a b c : Nat) : (a * b) * c = a * (b * c) := by
{{PROOF}}
