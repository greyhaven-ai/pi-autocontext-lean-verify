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
