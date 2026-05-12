set_option linter.unusedSimpArgs false

/-- Slow append over Nat lists. -/
def appendSlow : List Nat -> List Nat -> List Nat
| [], ys => ys
| x :: xs, ys => x :: appendSlow xs ys

/-- Slow length over Nat lists. -/
def lengthSlow : List Nat -> Nat
| [] => 0
| _ :: xs => Nat.succ (lengthSlow xs)

/-- Slow sum over Nat lists. -/
def sumSlow : List Nat -> Nat
| [] => 0
| x :: xs => x + sumSlow xs

/-- Count occurrences of a target Nat in a list, using local recursion. -/
def countSlow (target : Nat) : List Nat -> Nat
| [] => 0
| x :: xs => (if x = target then 1 else 0) + countSlow target xs

/-- Keep elements equal to the target. -/
def keepEqSlow (target : Nat) : List Nat -> List Nat
| [] => []
| x :: xs => if x = target then x :: keepEqSlow target xs else keepEqSlow target xs

/-- Drop elements equal to the target. -/
def dropEqSlow (target : Nat) : List Nat -> List Nat
| [] => []
| x :: xs => if x = target then dropEqSlow target xs else x :: dropEqSlow target xs

/-- Binary tree carrying Nat values. -/
inductive NatTree where
| leaf : NatTree
| node : NatTree -> Nat -> NatTree -> NatTree

open NatTree

/-- Mirror a tree. -/
def mirror : NatTree -> NatTree
| leaf => leaf
| node left value right => node (mirror right) value (mirror left)

/-- In-order flattening of a tree. -/
def flatten : NatTree -> List Nat
| leaf => []
| node left value right => appendSlow (flatten left) (value :: flatten right)

/-- Challenge v16: compact first-order Nat scalar packer plus append/filter helper lemmas. -/
theorem orderLengthCountSum_with_nat_scalar_packer (target : Nat) (tree : NatTree)
    (append_count : ∀ as bs : List Nat,
      countSlow target (appendSlow as bs) = countSlow target as + countSlow target bs)
    (append_length : ∀ as bs : List Nat,
      lengthSlow (appendSlow as bs) = lengthSlow as + lengthSlow bs)
    (append_sum : ∀ as bs : List Nat,
      sumSlow (appendSlow as bs) = sumSlow as + sumSlow bs)
    (keep_append : ∀ as bs : List Nat,
      keepEqSlow target (appendSlow as bs) = appendSlow (keepEqSlow target as) (keepEqSlow target bs))
    (drop_append : ∀ as bs : List Nat,
      dropEqSlow target (appendSlow as bs) = appendSlow (dropEqSlow target as) (dropEqSlow target bs))
    (packMetricScalars : ∀ lk lk' ld ld' ck ck' cd cd' sk sk' sd sd' : Nat,
      lk = lk' → ld = ld' → ck = ck' → cd = cd' → sk = sk' → sd = sd' →
      (lk = lk' ∧ ld = ld') ∧ (ck = ck' ∧ cd = cd') ∧ (sk = sk' ∧ sd = sd')) :
    (lengthSlow (keepEqSlow target (flatten (mirror tree))) =
        lengthSlow (keepEqSlow target (flatten tree)) ∧
      lengthSlow (dropEqSlow target (flatten (mirror tree))) =
        lengthSlow (dropEqSlow target (flatten tree))) ∧
      (countSlow target (keepEqSlow target (flatten (mirror tree))) =
        countSlow target (keepEqSlow target (flatten tree)) ∧
      countSlow target (dropEqSlow target (flatten (mirror tree))) =
        countSlow target (dropEqSlow target (flatten tree))) ∧
      (sumSlow (keepEqSlow target (flatten (mirror tree))) =
        sumSlow (keepEqSlow target (flatten tree)) ∧
      sumSlow (dropEqSlow target (flatten (mirror tree))) =
        sumSlow (dropEqSlow target (flatten tree))) := by
{{PROOF}}
