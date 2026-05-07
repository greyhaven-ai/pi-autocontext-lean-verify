# Compact Lean proof playbook v1

Use these only as proof-search guidance. The fixed theorem template still cannot be changed. Lean verification is the only success criterion.

## Core proof patterns

### Nat recursive normalization

For recursive Nat functions over `n`, try induction on the structurally recursive argument and simplify with the function, the induction hypothesis, and arithmetic normalization lemmas.

```lean
induction n with
| zero => rfl
| succ n ih =>
    simp [functionName, ih, Nat.mul_succ, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

If there is no multiplication, omit `Nat.mul_succ`.

### Custom multiplication/additive recursion

For custom multiplication-like functions, induce on the argument that the definition structurally consumes. If a stuck goal contains reordered addition such as `b + a`, try switching induction variables.

```lean
induction b with
| zero =>
    simp [mulSlow]
| succ b ih =>
    simp [mulSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

### List recursion over slow append/map/length/sum

For custom list functions, induce on the list consumed by the outer recursive definition.

```lean
induction xs with
| nil =>
    simp [appendSlow, lengthSlow]
| cons x xs ih =>
    simp [appendSlow, lengthSlow, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

Replace `lengthSlow` with the local function names, e.g. `sumSlow`, `mapDoubleSlow`, `revSlow`.

### Tree mirror/measure proofs

For tree measure preservation under mirror, induce on the tree and simplify both mirror and measure definitions with both induction hypotheses and additive normalization.

```lean
induction tree with
| leaf => rfl
| node left value right ihLeft ihRight =>
    simp [mirror, treeSize, ihLeft, ihRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
```

Replace `treeSize` with the local measure function, e.g. `leaves`.

### Local helper lemma for repeated intermediate facts

When the final goal repeats a fact such as `measure (mirror tree) = measure tree`, introduce a local helper by induction, then finish with `simp [h]`.

```lean
have h : measure (mirror tree) = measure tree := by
  induction tree with
  | leaf => rfl
  | node left value right ihLeft ihRight =>
      simp [mirror, measure, ihLeft, ihRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
simp [h]
```

### Built-in distribution

For plain Nat multiplication distribution, prefer the built-in theorem instead of induction.

```lean
rw [Nat.mul_add]
```

or

```lean
rw [Nat.add_mul]
```
