#!/usr/bin/env python3
"""Run an ordered playbook-transfer Lean proof experiment.

This is an external experiment harness. It keeps an explicit Markdown playbook of
verified proof patterns discovered from earlier fixtures and feeds that playbook
into later autocontext/Pi proof attempts.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

from experiment_common import (
    ROOT,
    aggregate_feature_usage,
    aggregate_proof_edit_usage,
    concise_verifier_feedback,
    history_item,
    history_summary,
    load_manifest,
    load_template,
    proof_edit_metrics,
    proof_edit_summary_from_attempts,
    proof_edit_summary_text,
    proof_feature_summary,
    proof_features,
    proof_preview,
    resolve_run_root,
    selected_fixtures,
    verify_attempt,
)
from prove_with_autocontext import build_rubric, run_autoctx_repair


def fixture_def_names(template: str) -> list[str]:
    return re.findall(r"^def\s+(\w+)\b", template, flags=re.MULTILINE)


def detected_lemmas(proof: str) -> list[str]:
    features = proof_features(proof)
    lemmas = list(features.get("lemmas") or [])
    if features.get("uses_omega") and "omega" not in lemmas:
        lemmas.append("omega")
    return lemmas


def learned_entry(*, fixture: str, proof: str) -> dict[str, Any]:
    template = load_template(fixture)
    defs = fixture_def_names(template)
    features = proof_features(proof)
    lemmas = detected_lemmas(proof)
    has_induction = bool(features.get("uses_induction"))
    uses_simp = bool(features.get("uses_simp"))
    uses_rw = bool(features.get("uses_rw"))
    if (
        has_induction
        and uses_simp
        and {
            "Nat.add_assoc",
            "Nat.add_comm",
            "Nat.add_left_comm",
        }.issubset(set(lemmas))
    ):
        rule = (
            "For recursive additive successor proofs, after induction and applying the IH, "
            "try `simp [functionName, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]`."
        )
    elif "omega" in lemmas:
        rule = (
            "If additive normalization remains after unfolding/induction, try `omega`."
        )
    elif has_induction and uses_rw:
        rule = "For recursive definitions, induction plus rewriting the recursive equation and IH often exposes arithmetic normalization."
    else:
        rule = "Use the verified proof shape as a local example for related fixtures."
    return {
        "fixture": fixture,
        "definitions": defs,
        "lemmas": lemmas,
        "features": features,
        "feature_summary": proof_feature_summary(features),
        "uses_induction": has_induction,
        "uses_simp": uses_simp,
        "uses_rw": uses_rw,
        "rule": rule,
        "proof": proof,
    }


def count_seed_entries(seed_playbook: str) -> int:
    return len(re.findall(r"^###\s+", seed_playbook, flags=re.MULTILINE))


def render_playbook(entries: list[dict[str, Any]], *, seed_playbook: str = "") -> str:
    seed_playbook = seed_playbook.strip()
    if not entries and not seed_playbook:
        return "No verified proof patterns yet."

    lines = [
        "# Learned Lean proof playbook",
        "",
        "Use these only as proof-search guidance. The fixed theorem template still cannot be changed.",
        "",
    ]
    if seed_playbook:
        lines.extend(
            [
                "## Seeded verified playbook",
                "",
                seed_playbook,
                "",
            ]
        )
    if entries:
        unique_rules: list[str] = []
        for entry in entries:
            rule = entry["rule"]
            if rule not in unique_rules:
                unique_rules.append(rule)
        lines.extend(["## New rules learned in this run", ""])
        for rule in unique_rules:
            lines.append(f"- {rule}")
        lines.extend(["", "## Newly verified examples from this run", ""])
        for entry in entries[-6:]:
            defs = ", ".join(entry.get("definitions") or []) or "none"
            lemmas = (
                entry.get("feature_summary")
                or ", ".join(entry.get("lemmas") or [])
                or "none"
            )
            proof = entry["proof"].strip()
            if len(proof) > 1600:
                proof = proof[:1600] + "\n-- truncated in playbook"
            lines.extend(
                [
                    f"### {entry['fixture']}",
                    "",
                    f"- definitions: {defs}",
                    f"- notable lemmas/tactics: {lemmas}",
                    "",
                    "```lean",
                    proof,
                    "```",
                    "",
                ]
            )
    else:
        lines.extend(["## Newly verified examples from this run", "", "None yet.", ""])
    return "\n".join(lines)


DIVERSITY_GUARD_TEXT = """Induction-diversity guard:
- The playbook is guidance, not a template to repeat blindly.
- Before choosing an induction, inspect which argument each recursive definition structurally consumes.
- If the target contains multiple variables, sums, or nested recursive calls, consider a different induction variable than the examples used.
- If Lean feedback shows a swapped/reordered recursive goal such as `f (b + a) ... = ...`, do not repeat the same induction pattern; try an induction variable that aligns the recursive argument, or use `rw [Nat.succ_add]` / `rw [Nat.add_succ]` before simplification.
- Prefer the smallest proof that fits the current theorem, even if it differs from the seeded examples.
"""


def induction_variables(proof: str) -> list[str]:
    return re.findall(r"\binduction\s+([A-Za-z_][A-Za-z0-9_']*)\s+with", proof)


def _lean_feedback_text(*results: dict[str, Any] | None) -> str:
    parts: list[str] = []
    for result in results:
        if not result:
            continue
        for key in ("stdout", "stderr"):
            value = result.get(key)
            if value:
                parts.append(str(value))
    return "\n".join(parts)


def theorem_parameters(template: str) -> list[dict[str, str]]:
    theorem_matches = list(
        re.finditer(
            r"\btheorem\s+\w+\s+((?:\([^)]*\)\s*)+)\s*:",
            template,
            flags=re.DOTALL,
        )
    )
    if not theorem_matches:
        return []
    prefix = theorem_matches[-1].group(1)
    parameters: list[dict[str, str]] = []
    for group in re.findall(r"\(([^:()]+)\s*:\s*([^()]+)\)", prefix):
        names_text, type_text = group
        type_name = type_text.strip()
        for name in names_text.split():
            if re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", name):
                parameters.append({"name": name, "type": type_name})
    return parameters


def theorem_variables(template: str) -> list[str]:
    return [parameter["name"] for parameter in theorem_parameters(template)]


def alternate_strategy_hints(
    *,
    fixture: str,
    proof: str,
    verification: dict[str, Any],
    primary_candidate: str,
    primary_preflight: dict[str, Any] | None,
) -> dict[str, Any]:
    """Infer compact alternate-strategy hints from Lean feedback.

    These are prompt-routing aids only. They never count as success; the next proof
    still has to pass the fixed Lean verifier.
    """

    failed_candidate = primary_candidate.strip() or proof.strip()
    used_inductions = induction_variables(failed_candidate)
    template = load_template(fixture)
    variables = theorem_variables(template)
    variable_set = set(variables)
    feedback = _lean_feedback_text(verification, primary_preflight)
    suggestions: list[str] = []
    evidence: list[str] = []
    for left, right in re.findall(
        r"\b([A-Za-z_][A-Za-z0-9_']*)\s*\+\s*([A-Za-z_][A-Za-z0-9_']*)\b",
        feedback,
    ):
        if right in used_inductions and left not in used_inductions:
            if not variable_set or left in variable_set:
                if left not in suggestions:
                    suggestions.append(left)
                    evidence.append(f"{left} + {right}")
    strategy = "induction_variable_swap" if suggestions else "generic_alternate"
    return {
        "strategy": strategy,
        "used_inductions": used_inductions,
        "suggested_inductions": suggestions,
        "evidence": evidence,
        "definition_names": fixture_def_names(template),
    }


def alternate_strategy_hint_text(hints: dict[str, Any]) -> str:
    if hints.get("strategy") != "induction_variable_swap":
        return "No high-confidence induction-variable swap was inferred from the Lean feedback."
    used = ", ".join(hints.get("used_inductions") or []) or "unknown"
    suggested = ", ".join(hints.get("suggested_inductions") or []) or "unknown"
    evidence = (
        ", ".join(hints.get("evidence") or []) or "reordered addition in the stuck goal"
    )
    defs = ", ".join(hints.get("definition_names") or []) or "the recursive definitions"
    return "\n".join(
        [
            "High-confidence induction-variable diagnosis from Lean feedback:",
            f"- The failed proof induced on: {used}.",
            f"- The stuck goal contains reordered addition evidence: {evidence}.",
            f"- For the alternate proof, do NOT induce on {used}; try induction on {suggested} first.",
            f"- Keep the replacement compact: unfold/simplify `{defs}` with `ih` and `Nat.add_assoc` before adding broader commutativity lemmas.",
        ]
    )


def nat_induction_candidate(variable: str, definitions: list[str]) -> str:
    simp_defs = ", ".join(definitions)
    base_simp = f"simp [{simp_defs}]" if simp_defs else "simp"
    step_simp = (
        f"simp [{simp_defs}, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]"
        if simp_defs
        else "simp [ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]"
    )
    return "\n".join(
        [
            f"induction {variable} with",
            "| zero =>",
            f"    {base_simp}",
            f"| succ {variable} ih =>",
            f"    {step_simp}",
        ]
    )


def local_theorem_names(template: str) -> list[str]:
    names = re.findall(r"^theorem\s+(\w+)\b", template, flags=re.MULTILINE)
    return names[:-1]


def list_induction_candidate(
    variable: str, definitions: list[str], helper_theorems: list[str]
) -> str:
    base_items = (
        definitions
        + helper_theorems
        + [
            "Nat.add_assoc",
            "Nat.add_comm",
            "Nat.add_left_comm",
        ]
    )
    step_items = (
        definitions
        + helper_theorems
        + [
            "ih",
            "Nat.add_assoc",
            "Nat.add_comm",
            "Nat.add_left_comm",
        ]
    )
    base_simp = f"simp [{', '.join(base_items)}]" if base_items else "simp"
    step_simp = f"simp [{', '.join(step_items)}]" if step_items else "simp [ih]"
    return "\n".join(
        [
            f"induction {variable} with",
            "| nil =>",
            f"    {base_simp}",
            f"| cons x {variable} ih =>",
            f"    {step_simp}",
        ]
    )


def inductive_constructors(template: str, type_name: str) -> list[dict[str, Any]]:
    block_match = re.search(
        rf"^inductive\s+{re.escape(type_name)}\s+where\n(?P<body>(?:^\|.*\n?)+)",
        template,
        flags=re.MULTILINE,
    )
    if not block_match:
        return []
    constructors: list[dict[str, Any]] = []
    for line in block_match.group("body").splitlines():
        match = re.match(r"^\|\s+(\w+)\s*:\s*(.+)$", line.strip())
        if not match:
            continue
        name = match.group(1)
        signature = match.group(2)
        parts = [part.strip() for part in signature.split("->")]
        arg_types = parts[:-1]
        recursive_positions = [
            index for index, arg_type in enumerate(arg_types) if arg_type == type_name
        ]
        constructors.append(
            {
                "name": name,
                "arg_types": arg_types,
                "recursive_positions": recursive_positions,
            }
        )
    return constructors


def helper_lemma_candidates(
    *, template: str, hints: dict[str, Any], feedback: str
) -> list[dict[str, str]]:
    parameters = {
        parameter["name"]: parameter["type"]
        for parameter in theorem_parameters(template)
    }
    definitions = list(hints.get("definition_names") or [])
    simp_items = definitions + [
        "{ihs}",
        "Nat.add_assoc",
        "Nat.add_comm",
        "Nat.add_left_comm",
    ]
    candidates: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for outer, inner, variable in re.findall(
        r"\b([A-Za-z_][A-Za-z0-9_']*)\s+\(([A-Za-z_][A-Za-z0-9_']*)\s+([A-Za-z_][A-Za-z0-9_']*)\)",
        feedback,
    ):
        key = (outer, inner, variable)
        if key in seen:
            continue
        seen.add(key)
        if not re.search(rf"\b{re.escape(outer)}\s+{re.escape(variable)}\b", feedback):
            continue
        type_name = parameters.get(variable)
        if not type_name:
            continue
        constructors = inductive_constructors(template, type_name)
        if not constructors:
            continue
        branches: list[str] = []
        for constructor in constructors:
            arg_names = [
                f"x{index}" for index, _ in enumerate(constructor["arg_types"])
            ]
            ih_names = [f"ih{index}" for index in constructor["recursive_positions"]]
            binder_text = " ".join(arg_names + ih_names)
            branch_head = f"| {constructor['name']}{(' ' + binder_text) if binder_text else ''} =>"
            if not arg_names:
                branches.extend([branch_head, "    rfl"])
                continue
            ih_text = ", ".join(ih_names)
            simp_text = ", ".join(
                item for item in simp_items if item != "{ihs}" or ih_text
            ).replace("{ihs}", ih_text)
            branches.extend([branch_head, f"    simp [{simp_text}]"])
        proof = "\n".join(
            [
                f"have h : {outer} ({inner} {variable}) = {outer} {variable} := by",
                f"  induction {variable} with",
                *[f"  {line}" for line in branches],
                "simp [h]",
            ]
        )
        candidates.append(
            {
                "label": f"helper_{outer}_{inner}_{variable}",
                "proof": proof,
            }
        )
    return candidates


def build_strategy_hint_candidates(
    *, fixture: str, hints: dict[str, Any], verification: dict[str, Any]
) -> list[dict[str, str]]:
    """Build conservative verifier-checked candidates from strategy hints.

    These are opt-in candidate proofs only. A candidate is used only if Lean accepts
    it in the fixed theorem template; otherwise the runner falls back to Pi repair.
    """

    template = load_template(fixture)
    definitions = list(hints.get("definition_names") or [])
    helper_theorems = local_theorem_names(template)
    candidates: list[dict[str, str]] = []
    if hints.get("strategy") == "induction_variable_swap":
        for variable in hints.get("suggested_inductions") or []:
            candidates.append(
                {
                    "label": f"induction_variable_swap_{variable}",
                    "proof": nat_induction_candidate(variable, definitions),
                }
            )
    elif hints.get("strategy") == "generic_alternate":
        for parameter in theorem_parameters(template):
            variable = parameter["name"]
            if parameter["type"] == "Nat":
                candidates.append(
                    {
                        "label": f"nat_induction_{variable}",
                        "proof": nat_induction_candidate(variable, definitions),
                    }
                )
            elif parameter["type"].startswith("List "):
                candidates.append(
                    {
                        "label": f"list_induction_{variable}",
                        "proof": list_induction_candidate(
                            variable, definitions, helper_theorems
                        ),
                    }
                )
        candidates.extend(
            helper_lemma_candidates(
                template=template,
                hints=hints,
                feedback=_lean_feedback_text(verification),
            )
        )
    return candidates


def build_strategy_hint_candidate(hints: dict[str, Any]) -> str:
    """Backward-compatible single-candidate helper for ad hoc debugging."""

    if hints.get("strategy") != "induction_variable_swap":
        return ""
    suggested = list(hints.get("suggested_inductions") or [])
    if len(suggested) != 1:
        return ""
    return nat_induction_candidate(
        suggested[0], list(hints.get("definition_names") or [])
    )


def repair_result_from_candidate(
    *, current_proof: str, candidate: str, source: str
) -> dict[str, Any]:
    edit_from_current = proof_edit_metrics(current_proof, candidate)
    return {
        "exit_code": 0,
        "timed_out": False,
        "elapsed_seconds": 0,
        "extracted_proof": candidate,
        "extracted_proof_features": proof_features(candidate),
        "extracted_proof_feature_summary": proof_feature_summary(candidate),
        "edit_from_current": edit_from_current,
        "edit_from_current_summary": proof_edit_summary_text(edit_from_current),
        "source": source,
    }


def try_strategy_hint_candidates(
    *,
    fixture: str,
    verification: dict[str, Any],
    current_proof: str,
    attempt_dir: Path,
    strategy_hints: dict[str, Any],
    directory_prefix: str,
    source_prefix: str,
) -> dict[str, Any]:
    """Generate conservative candidates, Lean-check them, and return first pass.

    This helper never treats a generated proof as successful on its own. The
    returned `used` flag is true only when the fixed Lean verifier accepted the
    candidate.
    """

    hint_results: list[dict[str, Any]] = []
    for hint_index, hint_candidate in enumerate(
        build_strategy_hint_candidates(
            fixture=fixture,
            hints=strategy_hints,
            verification=verification,
        )
    ):
        hint_proof = hint_candidate["proof"]
        hint_verification = verify_attempt(
            fixture=fixture,
            proof=hint_proof,
            attempt_dir=attempt_dir / f"{directory_prefix}_{hint_index:02d}",
        )
        hint_result = {
            "label": hint_candidate["label"],
            "proof": hint_proof,
            "proof_features": proof_features(hint_proof),
            "proof_feature_summary": proof_feature_summary(hint_proof),
            "verification": hint_verification,
            "ok": bool(hint_verification.get("ok")),
        }
        hint_results.append(hint_result)
        if hint_verification.get("ok"):
            return {
                "candidates": hint_results,
                "used": True,
                "used_label": hint_candidate["label"],
                "proof": hint_proof,
                "repair": repair_result_from_candidate(
                    current_proof=current_proof,
                    candidate=hint_proof,
                    source=f"{source_prefix}:{hint_candidate['label']}",
                ),
            }
    return {
        "candidates": hint_results,
        "used": False,
        "used_label": None,
        "proof": "",
        "repair": None,
    }


def build_alternate_repair_prompt(
    *,
    fixture: str,
    proof: str,
    verification: dict[str, Any],
    attempt_index: int,
    history: list[dict[str, Any]],
    playbook: str,
    primary_candidate: str,
    primary_preflight: dict[str, Any] | None,
    alternate_reason: list[str],
    strategy_hints: dict[str, Any] | None = None,
) -> str:
    failed_candidate = primary_candidate.strip() or proof.strip()
    used_inductions = induction_variables(failed_candidate)
    induction_note = (
        f"The failed candidate used induction on: {', '.join(used_inductions)}. Try a different induction variable if the recursive argument is misaligned."
        if used_inductions
        else "The failed candidate did not clearly use induction. Consider induction or a local helper lemma if the theorem is recursive."
    )
    preflight_text = (
        concise_verifier_feedback(primary_preflight)
        if primary_preflight
        else "No primary-candidate preflight was available."
    )
    reason_text = (
        "; ".join(alternate_reason)
        or "primary repair did not produce a verified candidate"
    )
    strategy_hints = strategy_hints or alternate_strategy_hints(
        fixture=fixture,
        proof=proof,
        verification=verification,
        primary_candidate=primary_candidate,
        primary_preflight=primary_preflight,
    )
    strategy_text = alternate_strategy_hint_text(strategy_hints)
    if strategy_hints.get("strategy") == "induction_variable_swap":
        suggested = ", ".join(strategy_hints.get("suggested_inductions") or [])
        used = ", ".join(strategy_hints.get("used_inductions") or [])
        defs = ", ".join(strategy_hints.get("definition_names") or [])
        return f"""The previous repair path exposed an induction-variable mismatch. Produce a materially different Lean 4 proof body.

You are not allowed to change the theorem template. Output only a corrected proof body for the `{{PROOF}}` placeholder.

Fixture: {fixture}
Attempt index: {attempt_index}
Alternate retry reason: {reason_text}

{strategy_text}

Fixed theorem template:
```lean
{load_template(fixture)}
```

Failed proof body:
```lean
{failed_candidate or proof.strip()}
```

Lean verifier feedback:
```text
{concise_verifier_feedback(verification)}
```

Targeted alternate requirements:
- Output ONLY a Lean proof body, preferably in one fenced Lean code block.
- Do NOT repeat `induction {used}`.
- Start by trying `induction {suggested} with`.
- In the base case, try `simp [{defs}]` if applicable.
- In the successor case, try `simp [{defs}, ih, Nat.add_assoc]` before adding broader arithmetic lemmas.
- Do not use `sorry`, `admit`, `axiom`, `unsafe`, new imports, or a modified theorem statement.
- Use Lean core/Init facts only; no Mathlib imports.
"""
    return f"""The previous repair path did not produce a Lean-checking proof. Produce a materially different Lean 4 proof body.

You are not allowed to change the theorem template. Output only a corrected proof body for the `{{PROOF}}` placeholder.

Fixture: {fixture}
Attempt index: {attempt_index}
Alternate retry reason: {reason_text}

The seeded playbook or primary repair path has already failed for this attempt. Do not rely on the full playbook context now; focus on the current theorem and Lean goal.

Compact playbook reminders only:
- Recursive additive normalization often uses induction plus `simp [..., ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]`.
- Multiplication-shift proofs sometimes need `Nat.mul_succ` or `Nat.mul_add`.
- Tree/list proofs may need a local helper lemma proved by induction, then a final `simp [h]`.

Fixed theorem template:
```lean
{load_template(fixture)}
```

Original proof body before repair:
```lean
{proof.strip()}
```

Lean verifier feedback for the original proof:
```text
{concise_verifier_feedback(verification)}
```

Primary repair candidate that failed or was unusable:
```lean
{failed_candidate or "<no candidate extracted>"}
```

Lean feedback for the primary repair candidate:
```text
{preflight_text}
```

Recent attempt history:
{history_summary(history)}

Structured alternate-strategy requirements:
- Do NOT repeat the same failed proof shape.
- {induction_note}
- If a recursive definition consumes one argument structurally but the failed candidate induced on another/misaligned expression, switch induction variables.
- If the goal repeats a useful intermediate fact, introduce a local `have h : ... := by` helper lemma, prove it by induction, then finish with `simp [h]`.
- If the failed goal contains reordered addition such as `b + a`, consider whether the induction variable should be `b`, or whether `rw [Nat.succ_add]`, `rw [Nat.add_succ]`, `Nat.add_assoc`, or `Nat.add_comm` is needed.
- Output ONLY the proof body, preferably in one fenced Lean code block.
- Do not include prose outside the code block.
- Do not use `sorry`, `admit`, `axiom`, `unsafe`, new imports, or a modified theorem statement.
- Use Lean core/Init facts only; no Mathlib imports.
"""


def build_pregenerate_prompt(
    *, fixture: str, playbook: str, induction_diversity_guard: bool = False
) -> str:
    guard = f"\n{DIVERSITY_GUARD_TEXT}" if induction_diversity_guard else ""
    return f"""Use the accumulated Lean proof playbook to produce a proof body for the next fixed theorem.

Output only a proof body for the `{{PROOF}}` placeholder. Do not output prose, imports, a theorem statement, `sorry`, `admit`, `axiom`, or `unsafe`.

Accumulated playbook from earlier Lean-verified fixtures:
```text
{playbook}
```

Fixed theorem template:
```lean
{load_template(fixture)}
```

Hints:
- If this resembles a recursive additive normalization theorem, strongly consider induction followed by `simp` with the recursive function, `ih`, `Nat.add_assoc`, `Nat.add_comm`, and `Nat.add_left_comm`.
- If arithmetic normalization remains, consider `omega`.{guard}
"""


def build_repair_prompt(
    *,
    fixture: str,
    proof: str,
    verification: dict[str, Any],
    attempt_index: int,
    history: list[dict[str, Any]],
    playbook: str,
    induction_diversity_guard: bool = False,
) -> str:
    guard = f"\n{DIVERSITY_GUARD_TEXT}" if induction_diversity_guard else ""
    return f"""Repair this Lean 4 proof body using both the real Lean verifier feedback and the accumulated verified proof playbook.

You are not allowed to change the theorem template. Output only a corrected proof body for the `{{PROOF}}` placeholder.

Fixture: {fixture}
Attempt index: {attempt_index}

Accumulated playbook from earlier Lean-verified fixtures:
```text
{playbook}
```

Fixed theorem template:
```lean
{load_template(fixture)}
```

Current proof body:
```lean
{proof.strip()}
```

Lean verifier feedback for the current proof:
```text
{concise_verifier_feedback(verification)}
```

Recent attempt history:
{history_summary(history)}

Rules:
- Output ONLY the proof body, preferably in one fenced Lean code block.
- Do not include prose outside the code block.
- Do not use `sorry`, `admit`, `axiom`, `unsafe`, new imports, or a modified theorem statement.
- Use Lean core/Init facts only; no Mathlib imports.
- Prefer reusing playbook patterns only when they genuinely fit this theorem.{guard}
"""


def summarize_row(fixture_summary: dict[str, Any]) -> dict[str, Any]:
    features = fixture_summary.get("final_proof_features") or proof_features(
        fixture_summary.get("final_proof")
    )
    return {
        "fixture": fixture_summary["fixture"],
        "proved": fixture_summary["proved"],
        "final_attempt": fixture_summary.get("final_attempt"),
        "elapsed_seconds": fixture_summary.get("elapsed_seconds"),
        "playbook_entries_before": fixture_summary.get("playbook_entries_before"),
        "playbook_entries_after": fixture_summary.get("playbook_entries_after"),
        "pregenerated": bool(fixture_summary.get("pregenerate")),
        "final_proof": fixture_summary.get("final_proof"),
        "proof_features": features,
        "feature_summary": proof_feature_summary(features),
        "proof_edit_summary": fixture_summary.get("proof_edit_summary")
        or proof_edit_summary_from_attempts(fixture_summary),
        "summary_path": fixture_summary.get("summary_path"),
    }


def _extracted_proof(result: dict[str, Any] | None) -> str:
    return str((result or {}).get("extracted_proof") or "").strip()


def _is_rfl_proof(proof: str) -> bool:
    return proof.strip() == "rfl"


def _add_pi_call(metrics: dict[str, Any], result: dict[str, Any] | None) -> None:
    metrics["pi_calls"] += 1
    metrics["pi_elapsed_seconds"] = round(
        metrics["pi_elapsed_seconds"]
        + float((result or {}).get("elapsed_seconds") or 0),
        2,
    )


def aggregate_trigger_cost_metrics(
    fixture_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "fixtures": len(fixture_summaries),
        "pi_calls": 0,
        "pi_elapsed_seconds": 0.0,
        "main_lean_verifier_attempts": 0,
        "primary_preflight_verifier_attempts": 0,
        "strategy_hint_verifier_attempts": 0,
        "total_lean_verifier_attempts": 0,
        "pregenerate_calls": 0,
        "pregenerate_empty": 0,
        "pregenerate_rfl": 0,
        "pregenerate_nontrivial": 0,
        "primary_repair_calls": 0,
        "primary_repair_empty": 0,
        "primary_repair_rfl": 0,
        "primary_repair_unchanged": 0,
        "primary_repair_failed_preflight": 0,
        "primary_repair_passed_preflight": 0,
        "pre_repair_strategy_hint_candidates_generated": 0,
        "pre_repair_strategy_hint_candidates_passed": 0,
        "pre_repair_strategy_hint_candidates_failed": 0,
        "pre_repair_strategy_hint_candidates_used": 0,
        "strategy_hint_candidates_generated": 0,
        "strategy_hint_candidates_passed": 0,
        "strategy_hint_candidates_failed": 0,
        "strategy_hint_candidates_used": 0,
        "strategy_hint_candidate_labels_used": {},
        "alternate_pi_fallback_calls": 0,
        "alternate_pi_fallback_empty": 0,
        "alternate_pi_fallback_extracted": 0,
        "alternate_pi_fallback_succeeded_next_attempt": 0,
    }
    for fixture_summary in fixture_summaries:
        pregenerate = fixture_summary.get("pregenerate")
        if pregenerate:
            metrics["pregenerate_calls"] += 1
            _add_pi_call(metrics, pregenerate)
            pregenerated = _extracted_proof(pregenerate)
            if not pregenerated:
                metrics["pregenerate_empty"] += 1
            elif _is_rfl_proof(pregenerated):
                metrics["pregenerate_rfl"] += 1
            else:
                metrics["pregenerate_nontrivial"] += 1

        attempts = list(fixture_summary.get("attempts") or [])
        metrics["main_lean_verifier_attempts"] += len(attempts)
        for index, attempt in enumerate(attempts):
            repair = attempt.get("repair")
            primary = attempt.get("primary_repair")
            if (
                primary is None
                and repair
                and "strategy_hint_candidate" not in str(repair.get("source") or "")
            ):
                primary = repair
            if primary:
                metrics["primary_repair_calls"] += 1
                _add_pi_call(metrics, primary)
                primary_proof = _extracted_proof(primary)
                if not primary_proof:
                    metrics["primary_repair_empty"] += 1
                elif _is_rfl_proof(primary_proof):
                    metrics["primary_repair_rfl"] += 1
                if (
                    primary_proof
                    and primary_proof == str(attempt.get("proof") or "").strip()
                ):
                    metrics["primary_repair_unchanged"] += 1

            primary_preflight = attempt.get("primary_repair_preflight")
            if primary_preflight:
                metrics["primary_preflight_verifier_attempts"] += 1
                if primary_preflight.get("ok"):
                    metrics["primary_repair_passed_preflight"] += 1
                else:
                    metrics["primary_repair_failed_preflight"] += 1

            pre_hint_candidates = list(
                attempt.get("pre_repair_strategy_hint_candidates") or []
            )
            metrics["pre_repair_strategy_hint_candidates_generated"] += len(
                pre_hint_candidates
            )
            pre_hint_passed = sum(
                1 for candidate in pre_hint_candidates if candidate.get("ok")
            )
            metrics["pre_repair_strategy_hint_candidates_passed"] += pre_hint_passed
            metrics["pre_repair_strategy_hint_candidates_failed"] += (
                len(pre_hint_candidates) - pre_hint_passed
            )
            if attempt.get("pre_repair_strategy_hint_candidate_used"):
                metrics["pre_repair_strategy_hint_candidates_used"] += 1
                metrics["strategy_hint_candidates_used"] += 1
                label = str(
                    attempt.get("pre_repair_strategy_hint_candidate_used_label")
                    or "unknown"
                )
                labels = metrics["strategy_hint_candidate_labels_used"]
                labels[label] = labels.get(label, 0) + 1

            hint_candidates = pre_hint_candidates + list(
                attempt.get("strategy_hint_candidates") or []
            )
            if attempt.get("strategy_hint_candidate"):
                hint_candidates.append(attempt["strategy_hint_candidate"])
            metrics["strategy_hint_candidates_generated"] += len(hint_candidates)
            metrics["strategy_hint_verifier_attempts"] += len(hint_candidates)
            hint_passed = sum(1 for candidate in hint_candidates if candidate.get("ok"))
            metrics["strategy_hint_candidates_passed"] += hint_passed
            metrics["strategy_hint_candidates_failed"] += (
                len(hint_candidates) - hint_passed
            )
            if attempt.get("strategy_hint_candidate_used"):
                metrics["strategy_hint_candidates_used"] += 1
                label = str(
                    attempt.get("strategy_hint_candidate_used_label") or "unknown"
                )
                labels = metrics["strategy_hint_candidate_labels_used"]
                labels[label] = labels.get(label, 0) + 1

            alternate = attempt.get("alternate_repair")
            if alternate:
                metrics["alternate_pi_fallback_calls"] += 1
                _add_pi_call(metrics, alternate)
                if _extracted_proof(alternate):
                    metrics["alternate_pi_fallback_extracted"] += 1
                else:
                    metrics["alternate_pi_fallback_empty"] += 1
                if index + 1 < len(attempts) and attempts[index + 1].get("ok"):
                    metrics["alternate_pi_fallback_succeeded_next_attempt"] += 1
    metrics["total_lean_verifier_attempts"] = (
        metrics["main_lean_verifier_attempts"]
        + metrics["primary_preflight_verifier_attempts"]
        + metrics["strategy_hint_verifier_attempts"]
    )
    return metrics


def persist_transfer_summary(
    *,
    run_root: Path,
    transfer_summary: dict[str, Any],
    rows: list[dict[str, Any]],
    playbook_entries: list[dict[str, Any]],
    seed_entry_count: int = 0,
) -> None:
    transfer_summary["proved"] = sum(1 for row in rows if row["proved"])
    transfer_summary["failed"] = sum(1 for row in rows if not row["proved"])
    transfer_summary["learned_playbook_entries"] = len(playbook_entries)
    transfer_summary["final_playbook_entries"] = seed_entry_count + len(
        playbook_entries
    )
    transfer_summary["feature_usage"] = aggregate_feature_usage(rows)
    transfer_summary["proof_edit_usage"] = aggregate_proof_edit_usage(rows)
    transfer_summary["trigger_cost_metrics"] = aggregate_trigger_cost_metrics(
        list(transfer_summary.get("fixture_summaries") or [])
    )
    (run_root / "transfer_summary.json").write_text(
        json.dumps(transfer_summary, indent=2), encoding="utf-8"
    )
    write_transfer_report(run_root, transfer_summary)


def write_transfer_report(run_root: Path, transfer_summary: dict[str, Any]) -> None:
    lines = [
        "# Playbook transfer experiment",
        "",
        f"Run root: `{run_root}`",
        "",
        "## Summary",
        "",
        f"- Fixtures: {transfer_summary['total']}",
        f"- Proved: {transfer_summary['proved']}",
        f"- Failed: {transfer_summary['failed']}",
        f"- Seed playbook: {transfer_summary.get('seed_playbook_path') or 'none'}",
        f"- Seed playbook entries: {transfer_summary.get('seed_playbook_entries', 0)}",
        f"- Induction diversity guard: {transfer_summary.get('induction_diversity_guard', False)}",
        f"- Structured alternate retry: {transfer_summary.get('structured_alternate_retry', False)}",
        f"- Structured hint candidates: {transfer_summary.get('structured_hint_candidates', False)}",
        f"- Pre-repair hint candidates: {transfer_summary.get('pre_repair_hint_candidates', False)}",
        f"- Newly learned playbook entries: {transfer_summary.get('learned_playbook_entries', 0)}",
        f"- Final playbook entries: {transfer_summary['final_playbook_entries']}",
        "",
    ]
    metrics = transfer_summary.get("trigger_cost_metrics") or {}
    if metrics:
        lines.extend(
            [
                "## Trigger/cost metrics",
                "",
                f"- Pi calls: {metrics.get('pi_calls')} ({metrics.get('pi_elapsed_seconds')}s provider elapsed)",
                f"- Lean verifier attempts: {metrics.get('total_lean_verifier_attempts')} (main={metrics.get('main_lean_verifier_attempts')}, preflight={metrics.get('primary_preflight_verifier_attempts')}, hint={metrics.get('strategy_hint_verifier_attempts')})",
                f"- Pregenerate: calls={metrics.get('pregenerate_calls')}, empty={metrics.get('pregenerate_empty')}, rfl={metrics.get('pregenerate_rfl')}, nontrivial={metrics.get('pregenerate_nontrivial')}",
                f"- Primary repair: calls={metrics.get('primary_repair_calls')}, empty={metrics.get('primary_repair_empty')}, rfl={metrics.get('primary_repair_rfl')}, unchanged={metrics.get('primary_repair_unchanged')}, failed_preflight={metrics.get('primary_repair_failed_preflight')}, passed_preflight={metrics.get('primary_repair_passed_preflight')}",
                f"- Strategy hints: generated={metrics.get('strategy_hint_candidates_generated')}, passed={metrics.get('strategy_hint_candidates_passed')}, failed={metrics.get('strategy_hint_candidates_failed')}, used={metrics.get('strategy_hint_candidates_used')}, labels={metrics.get('strategy_hint_candidate_labels_used')}",
                f"- Pre-repair strategy hints: generated={metrics.get('pre_repair_strategy_hint_candidates_generated')}, passed={metrics.get('pre_repair_strategy_hint_candidates_passed')}, failed={metrics.get('pre_repair_strategy_hint_candidates_failed')}, used={metrics.get('pre_repair_strategy_hint_candidates_used')}",
                f"- Alternate Pi fallback: calls={metrics.get('alternate_pi_fallback_calls')}, empty={metrics.get('alternate_pi_fallback_empty')}, extracted={metrics.get('alternate_pi_fallback_extracted')}, succeeded_next_attempt={metrics.get('alternate_pi_fallback_succeeded_next_attempt')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Fixture results",
            "",
            "| Order | Fixture | Proved | Final attempt | Pregenerated | Entries before→after | Seconds | Features | Edit summary | Final proof |",
            "|---:|---|---:|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for index, row in enumerate(transfer_summary["rows"], start=1):
        lines.append(
            "| {order} | {fixture} | {proved} | {attempt} | {pregenerated} | {before}→{after} | {seconds} | {features} | {edit} | `{proof}` |".format(
                order=index,
                fixture=row["fixture"],
                proved="yes" if row["proved"] else "no",
                attempt=row.get("final_attempt"),
                pregenerated="yes" if row.get("pregenerated") else "no",
                before=row.get("playbook_entries_before"),
                after=row.get("playbook_entries_after"),
                seconds=row.get("elapsed_seconds"),
                features=row.get("feature_summary")
                or proof_feature_summary(row.get("final_proof")),
                edit=(row.get("proof_edit_summary") or {}).get("total_token_distance"),
                proof=proof_preview(row.get("final_proof"), limit=260),
            )
        )
    lines.append("")
    (run_root / "transfer_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(ROOT / "benchmark_manifest.json"))
    parser.add_argument("--fixtures", nargs="+", required=True)
    parser.add_argument("--initial-proof", default="rfl")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--provider", default="pi")
    parser.add_argument("--package-version", default="0.4.8")
    parser.add_argument("--run-root")
    parser.add_argument(
        "--seed-playbook",
        help="Path to an existing verified playbook.md to seed transfer before the first fixture.",
    )
    parser.add_argument(
        "--no-pregenerate",
        action="store_true",
        help="Do not generate a first candidate from the playbook before Lean verification.",
    )
    parser.add_argument(
        "--induction-diversity-guard",
        action="store_true",
        help="Ask Pi to reconsider induction variables and avoid blindly repeating seeded playbook patterns.",
    )
    parser.add_argument(
        "--structured-alternate-retry",
        action="store_true",
        help="If a primary repair is empty, unchanged, or fails preflight, run one targeted alternate-strategy repair before the next Lean attempt.",
    )
    parser.add_argument(
        "--structured-hint-candidates",
        action="store_true",
        help="Before launching alternate Pi repair, preflight a conservative Lean candidate synthesized from high-confidence strategy hints.",
    )
    parser.add_argument(
        "--pre-repair-hint-candidates",
        action="store_true",
        help="When structured hint candidates are enabled, try verifier-checked hint candidates before the primary Pi repair.",
    )
    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest))
    fixtures = selected_fixtures(manifest, args.fixtures)
    run_root = resolve_run_root(args.run_root, "playbook_transfer")
    run_root.mkdir(parents=True, exist_ok=True)

    seed_playbook_text = ""
    seed_playbook_entries = 0
    seed_playbook_path = None
    if args.seed_playbook:
        seed_path = Path(args.seed_playbook)
        seed_playbook_text = seed_path.read_text(encoding="utf-8")
        seed_playbook_entries = count_seed_entries(seed_playbook_text)
        seed_playbook_path = str(seed_path)

    playbook_entries: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    fixture_summaries: list[dict[str, Any]] = []
    rubric = (
        build_rubric()
        + " Reward effective reuse of the supplied verified proof playbook when appropriate."
    )

    transfer_summary: dict[str, Any] = {
        "type": "playbook-transfer",
        "run_root": str(run_root),
        "provider": args.provider,
        "package_version": args.package_version,
        "fixtures": [fixture["id"] for fixture in fixtures],
        "total": len(fixtures),
        "proved": 0,
        "failed": 0,
        "seed_playbook_path": seed_playbook_path,
        "seed_playbook_entries": seed_playbook_entries,
        "induction_diversity_guard": bool(args.induction_diversity_guard),
        "structured_alternate_retry": bool(args.structured_alternate_retry),
        "structured_hint_candidates": bool(args.structured_hint_candidates),
        "pre_repair_hint_candidates": bool(args.pre_repair_hint_candidates),
        "learned_playbook_entries": 0,
        "final_playbook_entries": seed_playbook_entries,
        "rows": rows,
        "fixture_summaries": fixture_summaries,
    }

    for fixture in fixtures:
        fixture_id = fixture["id"]
        started = time.time()
        fixture_dir = run_root / fixture_id
        fixture_dir.mkdir(parents=True, exist_ok=True)
        playbook_before = seed_playbook_entries + len(playbook_entries)
        playbook = render_playbook(playbook_entries, seed_playbook=seed_playbook_text)
        (run_root / "playbook.md").write_text(playbook, encoding="utf-8")
        (fixture_dir / "playbook_before.md").write_text(playbook, encoding="utf-8")

        proof = fixture.get("initial_proof", args.initial_proof)
        pregenerate_result: dict[str, Any] | None = None
        if (playbook_entries or seed_playbook_text.strip()) and not args.no_pregenerate:
            pregenerate_dir = fixture_dir / "pregenerate"
            pregenerate_result = run_autoctx_repair(
                prompt=build_pregenerate_prompt(
                    fixture=fixture_id,
                    playbook=playbook,
                    induction_diversity_guard=args.induction_diversity_guard,
                ),
                rubric=rubric,
                current_proof=proof,
                attempt_dir=pregenerate_dir,
                provider=args.provider,
                package_version=args.package_version,
                rounds=args.rounds,
                timeout=args.timeout,
            )
            generated = str(pregenerate_result.get("extracted_proof") or "").strip()
            if generated:
                proof = generated
            (fixture_dir / "pregenerate_result.json").write_text(
                json.dumps(pregenerate_result, indent=2), encoding="utf-8"
            )

        attempts: list[dict[str, Any]] = []
        history: list[dict[str, Any]] = []
        proved = False
        final_attempt: int | None = None
        final_proof = proof

        for attempt in range(args.max_attempts):
            attempt_dir = fixture_dir / f"attempt_{attempt:02d}"
            verification = verify_attempt(
                fixture=fixture_id,
                proof=proof,
                attempt_dir=attempt_dir,
            )
            attempt_summary: dict[str, Any] = {
                "attempt": attempt,
                "proof": proof,
                "proof_features": proof_features(proof),
                "proof_feature_summary": proof_feature_summary(proof),
                "ok": bool(verification.get("ok")),
                "verification": verification,
            }
            attempts.append(attempt_summary)
            history.append(history_item(attempt, proof, bool(verification.get("ok"))))
            if verification.get("ok"):
                proved = True
                final_attempt = attempt
                final_proof = proof
                break
            if attempt == args.max_attempts - 1:
                final_proof = proof
                break
            next_proof = ""
            repair: dict[str, Any] | None = None
            if args.pre_repair_hint_candidates and args.structured_hint_candidates:
                pre_repair_strategy_hints = alternate_strategy_hints(
                    fixture=fixture_id,
                    proof=proof,
                    verification=verification,
                    primary_candidate="",
                    primary_preflight=None,
                )
                attempt_summary["pre_repair_strategy_hints"] = pre_repair_strategy_hints
                pre_repair_hint_attempt = try_strategy_hint_candidates(
                    fixture=fixture_id,
                    verification=verification,
                    current_proof=proof,
                    attempt_dir=attempt_dir,
                    strategy_hints=pre_repair_strategy_hints,
                    directory_prefix="pre_repair_strategy_hint_candidate",
                    source_prefix="pre_repair_strategy_hint_candidate",
                )
                if pre_repair_hint_attempt["candidates"]:
                    attempt_summary["pre_repair_strategy_hint_candidates"] = (
                        pre_repair_hint_attempt["candidates"]
                    )
                if pre_repair_hint_attempt["used"]:
                    repair = pre_repair_hint_attempt["repair"]
                    next_proof = str(pre_repair_hint_attempt["proof"] or "").strip()
                    attempt_summary["repair"] = repair
                    attempt_summary["pre_repair_strategy_hint_candidate_used"] = True
                    attempt_summary["pre_repair_strategy_hint_candidate_used_label"] = (
                        pre_repair_hint_attempt["used_label"]
                    )

            if not next_proof:
                repair = run_autoctx_repair(
                    prompt=build_repair_prompt(
                        fixture=fixture_id,
                        proof=proof,
                        verification=verification,
                        attempt_index=attempt,
                        history=history,
                        playbook=playbook,
                        induction_diversity_guard=args.induction_diversity_guard,
                    ),
                    rubric=rubric,
                    current_proof=proof,
                    attempt_dir=attempt_dir,
                    provider=args.provider,
                    package_version=args.package_version,
                    rounds=args.rounds,
                    timeout=args.timeout,
                )
                attempt_summary["repair"] = repair
                next_proof = str(repair.get("extracted_proof") or "").strip()
                if args.structured_alternate_retry:
                    alternate_reason: list[str] = []
                    primary_preflight: dict[str, Any] | None = None
                    if not next_proof:
                        alternate_reason.append("primary repair returned no candidate")
                    elif next_proof.strip() == proof.strip():
                        alternate_reason.append(
                            "primary repair did not change the proof"
                        )
                    else:
                        primary_preflight = verify_attempt(
                            fixture=fixture_id,
                            proof=next_proof,
                            attempt_dir=attempt_dir / "primary_repair_preflight",
                        )
                        attempt_summary["primary_repair_preflight"] = primary_preflight
                        if not primary_preflight.get("ok"):
                            alternate_reason.append(
                                "primary repair candidate failed Lean preflight"
                            )
                    if alternate_reason:
                        strategy_hints = alternate_strategy_hints(
                            fixture=fixture_id,
                            proof=proof,
                            verification=verification,
                            primary_candidate=next_proof,
                            primary_preflight=primary_preflight,
                        )
                        attempt_summary["primary_repair"] = repair
                        attempt_summary["alternate_retry_reason"] = alternate_reason
                        attempt_summary["alternate_strategy_hints"] = strategy_hints
                        hint_candidate_used = False
                        if args.structured_hint_candidates:
                            hint_attempt = try_strategy_hint_candidates(
                                fixture=fixture_id,
                                verification=verification,
                                current_proof=next_proof or proof,
                                attempt_dir=attempt_dir,
                                strategy_hints=strategy_hints,
                                directory_prefix="strategy_hint_candidate",
                                source_prefix="strategy_hint_candidate",
                            )
                            if hint_attempt["candidates"]:
                                attempt_summary["strategy_hint_candidates"] = (
                                    hint_attempt["candidates"]
                                )
                            if hint_attempt["used"]:
                                repair = hint_attempt["repair"]
                                attempt_summary["repair"] = repair
                                attempt_summary["strategy_hint_candidate_used"] = True
                                attempt_summary[
                                    "strategy_hint_candidate_used_label"
                                ] = hint_attempt["used_label"]
                                hint_candidate_used = True
                                next_proof = str(hint_attempt["proof"] or "").strip()
                        if not hint_candidate_used:
                            alternate = run_autoctx_repair(
                                prompt=build_alternate_repair_prompt(
                                    fixture=fixture_id,
                                    proof=proof,
                                    verification=verification,
                                    attempt_index=attempt,
                                    history=history,
                                    playbook=playbook,
                                    primary_candidate=next_proof,
                                    primary_preflight=primary_preflight,
                                    alternate_reason=alternate_reason,
                                    strategy_hints=strategy_hints,
                                ),
                                rubric=rubric,
                                current_proof=next_proof or proof,
                                attempt_dir=attempt_dir / "alternate_repair",
                                provider=args.provider,
                                package_version=args.package_version,
                                rounds=args.rounds,
                                timeout=args.timeout,
                            )
                            attempt_summary["alternate_repair"] = alternate
                            alternate_proof = str(
                                alternate.get("extracted_proof") or ""
                            ).strip()
                            if alternate_proof:
                                repair = alternate
                                attempt_summary["repair"] = alternate
                                next_proof = alternate_proof
            if next_proof:
                attempt_summary["proof_edit"] = proof_edit_metrics(proof, next_proof)
                attempt_summary["proof_edit_summary"] = proof_edit_summary_text(
                    attempt_summary["proof_edit"]
                )
            proof = next_proof or proof
            final_proof = proof

        if proved:
            playbook_entries.append(
                learned_entry(fixture=fixture_id, proof=final_proof)
            )
        playbook_after = seed_playbook_entries + len(playbook_entries)
        playbook = render_playbook(playbook_entries, seed_playbook=seed_playbook_text)
        (run_root / "playbook.md").write_text(playbook, encoding="utf-8")
        (fixture_dir / "playbook_after.md").write_text(playbook, encoding="utf-8")
        elapsed = round(time.time() - started, 2)
        fixture_summary = {
            "fixture": fixture_id,
            "proved": proved,
            "final_attempt": final_attempt,
            "final_proof": final_proof,
            "final_proof_features": proof_features(final_proof),
            "final_proof_feature_summary": proof_feature_summary(final_proof),
            "elapsed_seconds": elapsed,
            "playbook_entries_before": playbook_before,
            "playbook_entries_after": playbook_after,
            "induction_diversity_guard": bool(args.induction_diversity_guard),
            "structured_alternate_retry": bool(args.structured_alternate_retry),
            "structured_hint_candidates": bool(args.structured_hint_candidates),
            "pre_repair_hint_candidates": bool(args.pre_repair_hint_candidates),
            "pregenerate": pregenerate_result,
            "attempts": attempts,
            "summary_path": str(fixture_dir / "summary.json"),
        }
        fixture_summary["proof_edit_summary"] = proof_edit_summary_from_attempts(
            fixture_summary
        )
        (fixture_dir / "summary.json").write_text(
            json.dumps(fixture_summary, indent=2), encoding="utf-8"
        )
        fixture_summaries.append(fixture_summary)
        rows.append(summarize_row(fixture_summary))
        persist_transfer_summary(
            run_root=run_root,
            transfer_summary=transfer_summary,
            rows=rows,
            playbook_entries=playbook_entries,
            seed_entry_count=seed_playbook_entries,
        )
        print(
            json.dumps(
                {
                    "fixture": fixture_id,
                    "proved": proved,
                    "final_attempt": final_attempt,
                    "playbook_entries": seed_playbook_entries + len(playbook_entries),
                }
            ),
            flush=True,
        )

    persist_transfer_summary(
        run_root=run_root,
        transfer_summary=transfer_summary,
        rows=rows,
        playbook_entries=playbook_entries,
        seed_entry_count=seed_playbook_entries,
    )
    print(json.dumps(transfer_summary, indent=2))
    return 0 if transfer_summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
