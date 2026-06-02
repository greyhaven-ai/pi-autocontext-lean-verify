# Formalization notes — session index

A running log of Lean/mathlib formalization sessions run through (or alongside)
this harness, so attempts are navigable and their hard-won lessons are reusable.

**How to use:** each session/attempt gets its own dated detail file in this
directory and one row below (newest first). Give every entry a stable `Session`
id (date + slug). Detail files carry the mathlib gotchas, methodology lessons,
and campaign status discovered in that session. Lean is always the oracle; these
notes are advisory and never assert a proof is correct.

| Session                                                                               | Date       | Campaign                                                                                                                           | Outcome                                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [2026-06-02-navier-stokes-energy-method](./2026-06-02-navier-stokes-energy-method.md) | 2026-06-02 | 3D incompressible Navier–Stokes energy method (Lean 4 / mathlib); plus shipping mathlib retrieval + index producer in this package | Energy method structurally complete and machine-checked (58 theorems), conditional on standard regularity (now dischargeable from `C²` + compact support). Explicitly **not** progress on the open Millennium problem. |
