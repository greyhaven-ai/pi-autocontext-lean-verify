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

/-- Challenge v17: compact pair+top packers plus detailed True proof-plan names; hints are proof-plan names only and carry no mathematical content. -/
theorem orderLengthCountSum_pair_top_packers_with_detailed_plan_hints (target : Nat) (tree : NatTree)
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
    (packPair : ∀ P Q : Prop, P → Q → P ∧ Q)
    (packMetricPairs : ∀ P Q R : Prop, P → Q → R → P ∧ Q ∧ R)
    (plan_induct_on_tree : True)
    (plan_leaf_simp_definitions : True)
    (plan_node_by_cases_value_eq_target : True)
    (plan_simp_mirror_flatten_keep_drop_append : True)
    (plan_normalize_nat_add_assoc_comm_left_comm : True)
    (plan_finish_with_metric_packers : True) :
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
