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
