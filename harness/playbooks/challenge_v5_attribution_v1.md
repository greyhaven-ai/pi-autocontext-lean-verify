# Learned Lean proof playbook

Use these only as proof-search guidance. The fixed theorem template still cannot be changed.

## Seeded verified playbook

# Learned Lean proof playbook

Use these only as proof-search guidance. The fixed theorem template still cannot be changed.

## Seeded verified playbook

# Learned Lean proof playbook

Use these only as proof-search guidance. The fixed theorem template still cannot be changed.

## Seeded verified playbook

# Learned Lean proof playbook

Use these only as proof-search guidance. The fixed theorem template still cannot be changed.

## Seeded verified playbook

# Learned Lean proof playbook

Use these only as proof-search guidance. The fixed theorem template still cannot be changed.

## Seeded verified playbook

# Learned Lean proof playbook

Use these only as proof-search guidance. The fixed theorem template still cannot be changed.

## General rules learned from verified proofs

- For recursive additive successor proofs, after induction and applying the IH, try `simp [functionName, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]`.

## Recently verified examples

### triple_shift_eq_three_mul_add_two

- definitions: tripleShift
- notable lemmas/tactics: induction, simp, rfl, Nat.mul_succ, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction n with
| zero => rfl
| succ n ih =>
    simp [tripleShift, ih, Nat.mul_succ, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### mul_slow_succ_right

- definitions: mulSlow
- notable lemmas/tactics: induction, simp, rfl, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction a with
| zero => rfl
| succ a ih =>
    simp [mulSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### quad_pair_eq_pair_sum

- definitions: quadPair
- notable lemmas/tactics: induction, simp, rfl, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction n with
| zero => rfl
| succ n ih =>
    simp [quadPair, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### tree_size_mirror_mirror

- definitions: mirror, treeSize
- notable lemmas/tactics: induction, simp, rfl, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction tree with
| leaf => rfl
| node left value right ihLeft ihRight =>
    simp [mirror, treeSize, ihLeft, ihRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### length_slow_append_slow

- definitions: lengthSlow, appendSlow
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction xs with
| nil =>
    simp [appendSlow, lengthSlow]
| cons x xs ih =>
    simp [appendSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### tri_nest_eq_right_nested

- definitions: triNest
- notable lemmas/tactics: induction, simp, rfl, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction n with
| zero => rfl
| succ n ih =>
    simp [triNest, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

## New rules learned in this run

- For recursive additive successor proofs, after induction and applying the IH, try `simp [functionName, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]`.
- Use the verified proof shape as a local example for related fixtures.

## Newly verified examples from this run

### challenge_sum_slow_map_succ

- definitions: lengthSlow, sumSlow, succMapSlow
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction xs with
| nil =>
    simp [succMapSlow, sumSlow, lengthSlow]
| cons x xs ih =>
    simp [succMapSlow, sumSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### challenge_tree_height_mirror

- definitions: mirror, height
- notable lemmas/tactics: induction, simp, rfl, Nat.max_comm

```lean
induction tree with
| leaf => rfl
| node left value right ihLeft ihRight =>
    simp [mirror, height, ihLeft, ihRight, Nat.max_comm]
```

### challenge_rev_map_double_slow

- definitions: appendSlow, revSlow, mapDoubleSlow
- notable lemmas/tactics: induction, simp, rfl

```lean
induction xs with
| nil => rfl
| cons x xs ih =>
    simp [revSlow, mapDoubleSlow, appendSlow, ih, mapDoubleAppendSlow]
```

## New rules learned in this run

- For recursive additive successor proofs, after induction and applying the IH, try `simp [functionName, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]`.
- Use the verified proof shape as a local example for related fixtures.

## Newly verified examples from this run

### challenge_v2_length_rev_no_helper

- definitions: lengthSlow, appendSlow, revSlow
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
have append_length : ∀ as bs : List Nat, lengthSlow (appendSlow as bs) = lengthSlow as + lengthSlow bs := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, lengthSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
induction xs with
| nil =>
    simp [revSlow, lengthSlow]
| cons x xs ih =>
    simp [revSlow, lengthSlow, append_length, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### challenge_v2_sum_rev_no_helper

- definitions: appendSlow, revSlow, sumSlow
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
have append_sum : ∀ as bs : List Nat, sumSlow (appendSlow as bs) = sumSlow as + sumSlow bs := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, sumSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, sumSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
induction xs with
| nil =>
    simp [revSlow, sumSlow]
| cons x xs ih =>
    simp [revSlow, sumSlow, append_sum, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### challenge_v2_map_succ_rev_no_helper

- definitions: appendSlow, revSlow, mapSuccSlow
- notable lemmas/tactics: induction, simp

```lean
have map_append : ∀ as bs : List Nat,
    mapSuccSlow (appendSlow as bs) = appendSlow (mapSuccSlow as) (mapSuccSlow bs) := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, mapSuccSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, mapSuccSlow, ih]
induction xs with
| nil =>
    simp [revSlow, mapSuccSlow]
| cons x xs ih =>
    simp [revSlow, mapSuccSlow, appendSlow, map_append, ih]
```

## New rules learned in this run

- Use the verified proof shape as a local example for related fixtures.

## Newly verified examples from this run

### challenge_v3_rev_acc_generalization

- definitions: appendSlow, revSlow, revAcc
- notable lemmas/tactics: induction, simp

```lean
have append_assoc : ∀ as bs cs : List Nat,
    appendSlow (appendSlow as bs) cs = appendSlow as (appendSlow bs cs) := by
  intro as
  induction as with
  | nil =>
      intro bs cs
      simp [appendSlow]
  | cons a as ih =>
      intro bs cs
      simp [appendSlow, ih]
have append_nil : ∀ as : List Nat, appendSlow as [] = as := by
  intro as
  induction as with
  | nil =>
      simp [appendSlow]
  | cons a as ih =>
      simp [appendSlow, ih]
have revAcc_eq : ∀ xs acc : List Nat, revAcc xs acc = appendSlow (revSlow xs) acc := by
  intro xs
  induction xs with
  | nil =>
      intro acc
      simp [revAcc, revSlow, appendSlow]
  | cons x xs ih =>
      intro acc
      simp [revAcc, revSlow, ih, append_assoc, appendSlow]
simpa [append_nil] using revAcc_eq xs []
```

### challenge_v3_sum_acc_generalization

- definitions: sumSlow, sumAcc
- notable lemmas/tactics: induction, simp, Nat.add_assoc

```lean
have h : ∀ xs acc, sumAcc xs acc = acc + sumSlow xs := by
  intro xs
  induction xs with
  | nil =>
      intro acc
      simp [sumAcc, sumSlow]
  | cons x xs ih =>
      intro acc
      simp [sumAcc, sumSlow, ih, Nat.add_assoc]
simpa using h xs 0
```

### challenge_v3_tree_flatten_mirror

- definitions: appendSlow, revSlow, mirror, flatten
- notable lemmas/tactics: induction, simp

```lean
have append_assoc : ∀ as bs cs : List Nat,
    appendSlow (appendSlow as bs) cs = appendSlow as (appendSlow bs cs) := by
  intro as
  induction as with
  | nil =>
      intro bs cs
      simp [appendSlow]
  | cons a as ih =>
      intro bs cs
      simp [appendSlow, ih]
have append_nil : ∀ as : List Nat, appendSlow as [] = as := by
  intro as
  induction as with
  | nil =>
      simp [appendSlow]
  | cons a as ih =>
      simp [appendSlow, ih]
have rev_append : ∀ as bs : List Nat,
    revSlow (appendSlow as bs) = appendSlow (revSlow bs) (revSlow as) := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, revSlow, append_nil]
  | cons a as ih =>
      intro bs
      simp [appendSlow, revSlow, ih, append_assoc]
induction tree with
| leaf =>
    simp [mirror, flatten, revSlow]
| node left value right ihLeft ihRight =>
    simp [mirror, flatten, revSlow, appendSlow, ihLeft, ihRight, rev_append, append_assoc]
```

### challenge_v3_map_rev_append_combined

- definitions: appendSlow, revSlow, mapDoubleSlow
- notable lemmas/tactics: induction, simp

```lean
have append_assoc : ∀ as bs cs : List Nat,
    appendSlow (appendSlow as bs) cs = appendSlow as (appendSlow bs cs) := by
  intro as
  induction as with
  | nil =>
      intro bs cs
      simp [appendSlow]
  | cons a as ih =>
      intro bs cs
      simp [appendSlow, ih]
have append_nil : ∀ as : List Nat, appendSlow as [] = as := by
  intro as
  induction as with
  | nil =>
      simp [appendSlow]
  | cons a as ih =>
      simp [appendSlow, ih]
have map_append : ∀ as bs : List Nat,
    mapDoubleSlow (appendSlow as bs) = appendSlow (mapDoubleSlow as) (mapDoubleSlow bs) := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, mapDoubleSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, mapDoubleSlow, ih]
have rev_append : ∀ as bs : List Nat,
    revSlow (appendSlow as bs) = appendSlow (revSlow bs) (revSlow as) := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, revSlow, append_nil]
  | cons a as ih =>
      intro bs
      simp [appendSlow, revSlow, ih, append_assoc]
simp [rev_append, map_append]
```

## New rules learned in this run

- For recursive additive successor proofs, after induction and applying the IH, try `simp [functionName, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]`.

## Newly verified examples from this run

### challenge_v4_count_acc_generalization

- definitions: countSlow, countAcc
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction xs generalizing acc with
| nil =>
    simp [countAcc, countSlow]
| cons x xs ih =>
    simp [countAcc, countSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### challenge_v4_count_rev_slow

- definitions: appendSlow, revSlow, countSlow
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
have append_count : ∀ as bs : List Nat,
    countSlow target (appendSlow as bs) = countSlow target as + countSlow target bs := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, countSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, countSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
induction xs with
| nil =>
    simp [revSlow, countSlow]
| cons x xs ih =>
    simp [revSlow, countSlow, append_count, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### challenge_v4_count_flatten_mirror

- definitions: appendSlow, countSlow, mirror, flatten
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
have append_count : ∀ as bs : List Nat,
    countSlow target (appendSlow as bs) = countSlow target as + countSlow target bs := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, countSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, countSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
induction tree with
| leaf =>
    simp [mirror, flatten, countSlow]
| node left value right ihLeft ihRight =>
    simp [mirror, flatten, countSlow, append_count, ihLeft, ihRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### challenge_v4_count_mapSucc_rev

- definitions: appendSlow, revSlow, mapSuccSlow, countSlow
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm, Nat.succ

```lean
have append_count : ∀ (t : Nat) (as bs : List Nat),
    countSlow t (appendSlow as bs) = countSlow t as + countSlow t bs := by
  intro t as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, countSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, countSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
have count_rev : ∀ (t : Nat) (as : List Nat), countSlow t (revSlow as) = countSlow t as := by
  intro t as
  induction as with
  | nil =>
      simp [revSlow, countSlow]
  | cons a as ih =>
      simp [revSlow, countSlow, append_count, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
have count_mapSucc : ∀ as : List Nat,
    countSlow (Nat.succ target) (mapSuccSlow as) = countSlow target as := by
  intro as
  induction as with
  | nil =>
      simp [mapSuccSlow, countSlow]
  | cons a as ih =>
      simp [mapSuccSlow, countSlow, ih]
simp [count_mapSucc, count_rev]
```

## New rules learned in this run

- For recursive additive successor proofs, after induction and applying the IH, try `simp [functionName, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]`.
- Use the verified proof shape as a local example for related fixtures.

## Newly verified examples from this run

### challenge_v5_tally_acc_pair

- definitions: countSlow, lengthSlow, tallyAcc
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
induction xs generalizing hits total with
| nil =>
    simp [tallyAcc, countSlow, lengthSlow]
| cons x xs ih =>
    simp [tallyAcc, countSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### challenge_v5_partition_count_length

- definitions: lengthSlow, countSlow, keepEqSlow, dropEqSlow
- notable lemmas/tactics: induction, simp, constructor, congrArg, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm, Nat.succ

```lean
induction xs with
| nil =>
    simp [keepEqSlow, dropEqSlow, countSlow, lengthSlow]
| cons x xs ih =>
    by_cases h : x = target
    · constructor
      · simp [keepEqSlow, countSlow, lengthSlow, h, ih.1, Nat.add_comm]
      · simpa [keepEqSlow, dropEqSlow, countSlow, lengthSlow, h, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using congrArg Nat.succ ih.2
    · constructor
      · simp [keepEqSlow, countSlow, lengthSlow, h, ih.1, Nat.add_comm]
      · simpa [keepEqSlow, dropEqSlow, countSlow, lengthSlow, h, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using congrArg Nat.succ ih.2
```

### challenge_v5_filter_rev_count_combo

- definitions: appendSlow, revSlow, countSlow, keepEqSlow
- notable lemmas/tactics: induction, simp, exact

```lean
have append_nil : ∀ as : List Nat, appendSlow as [] = as := by
  intro as
  induction as with
  | nil =>
      simp [appendSlow]
  | cons a as ih =>
      simp [appendSlow, ih]
have keep_append : ∀ as bs : List Nat,
    keepEqSlow target (appendSlow as bs) = appendSlow (keepEqSlow target as) (keepEqSlow target bs) := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, keepEqSlow]
  | cons a as ih =>
      intro bs
      by_cases h : a = target
      · simp [appendSlow, keepEqSlow, h, ih]
      · simp [appendSlow, keepEqSlow, h, ih]
have keep_rev : ∀ as : List Nat, keepEqSlow target (revSlow as) = revSlow (keepEqSlow target as) := by
  intro as
  induction as with
  | nil =>
      simp [revSlow, keepEqSlow]
  | cons a as ih =>
      by_cases h : a = target
      · simp [revSlow, keepEqSlow, keep_append, ih, h]
      · simp [revSlow, keepEqSlow, keep_append, ih, h, append_nil]
have count_keep : ∀ as : List Nat, countSlow target (keepEqSlow target as) = countSlow target as := by
  intro as
  induction as with
  | nil =>
      simp [keepEqSlow, countSlow]
  | cons a as ih =>
      by_cases h : a = target
      · simp [keepEqSlow, countSlow, h, ih]
      · simp [keepEqSlow, countSlow, h, ih]
exact ⟨keep_rev xs, count_keep xs⟩
```

### challenge_v5_tree_tally_mirror

- definitions: appendSlow, lengthSlow, countSlow, tallyAcc, mirror, flatten
- notable lemmas/tactics: induction, simp, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm

```lean
have tally_eq : ∀ xs hits total,
    tallyAcc target xs hits total = (countSlow target xs + hits, lengthSlow xs + total) := by
  intro xs
  induction xs with
  | nil =>
      intro hits total
      simp [tallyAcc, countSlow, lengthSlow]
  | cons x xs ih =>
      intro hits total
      simp [tallyAcc, countSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
have append_count : ∀ as bs : List Nat,
    countSlow target (appendSlow as bs) = countSlow target as + countSlow target bs := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, countSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, countSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
have append_length : ∀ as bs : List Nat,
    lengthSlow (appendSlow as bs) = lengthSlow as + lengthSlow bs := by
  intro as
  induction as with
  | nil =>
      intro bs
      simp [appendSlow, lengthSlow]
  | cons a as ih =>
      intro bs
      simp [appendSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
have count_mirror : ∀ tree : NatTree,
    countSlow target (flatten (mirror tree)) = countSlow target (flatten tree) := by
  intro tree
  induction tree with
  | leaf =>
      simp [mirror, flatten, countSlow]
  | node left value right ihLeft ihRight =>
      simp [mirror, flatten, countSlow, append_count, ihLeft, ihRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
have length_mirror : ∀ tree : NatTree,
    lengthSlow (flatten (mirror tree)) = lengthSlow (flatten tree) := by
  intro tree
  induction tree with
  | leaf =>
      simp [mirror
-- truncated in playbook
```
