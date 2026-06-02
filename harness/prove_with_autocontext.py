#!/usr/bin/env python3
"""Experiment-only Lean-in-the-loop proof repair with autocontext.

This is intentionally an external process, not an autocontext feature. The loop is:
verify proof with Lean -> feed Lean error to `autoctx improve` -> extract proof -> repeat.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from experiment_common import (
    ROOT,
    concise_verifier_feedback,
    history_item,
    history_summary,
    load_template,
    proof_edit_metrics,
    proof_edit_summary_from_attempts,
    proof_edit_summary_text,
    proof_feature_summary,
    proof_features,
    utc_stamp,
    verify_attempt,
)
import mathlib_retrieval
from extract_candidate_proof import extract
from process_utils import communicate_process_group, popen_process_group


def fenced(proof: str) -> str:
    return f"```lean\n{proof.strip()}\n```"


def build_repair_prompt(
    *,
    fixture: str,
    proof: str,
    verification: dict[str, Any],
    attempt_index: int,
    history: list[dict[str, Any]],
    lemma_block: str = "",
    allow_mathlib: bool = False,
) -> str:
    history_text = history_summary(history)
    # The default (Init-only) prompt is preserved byte-for-byte when no lemma
    # block is supplied and Mathlib is not allowed, so existing fixtures and
    # benchmarks are unaffected. The retrieved-lemma section and the relaxed
    # import rules only appear under the lean-mathlib profile. See issue #1.
    lemma_section = f"\n{lemma_block}\n" if lemma_block else ""
    if allow_mathlib:
        import_rules = (
            "- Do not use `sorry`, `admit`, `axiom`, `unsafe`, or a modified theorem statement.\n"
            "- Mathlib is available: you may use Mathlib lemmas and imports. "
            "Prefer the candidate lemmas listed above when one fits the goal."
        )
    else:
        import_rules = (
            "- Do not use `sorry`, `admit`, `axiom`, `unsafe`, new imports, or a modified theorem statement.\n"
            "- Use Lean core/Init facts only; no Mathlib imports."
        )
    return f"""Repair this Lean 4 proof body using the real Lean verifier feedback.

You are not allowed to change the theorem template. You must output only a corrected proof body for the `{{PROOF}}` placeholder.

Fixture: {fixture}
Attempt index: {attempt_index}

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
{lemma_section}
Recent attempt history:
{history_text}

Rules:
- Output ONLY the proof body, preferably in one fenced Lean code block.
- Do not include prose outside the code block.
{import_rules}
- If the error says a tactic failed, choose a different Lean proof strategy.
"""


def build_rubric() -> str:
    return """Score 1.0 only for a corrected Lean proof body that is likely to compile in the exact fixed theorem template and directly addresses the provided Lean error. Score 0 for prose, changed theorem statements, sorry/admit/axiom/unsafe, new imports, or a proof that repeats the same failing tactic without repair. Prefer concise Lean code in a fenced lean block."""


def run_autoctx_repair(
    *,
    prompt: str,
    rubric: str,
    current_proof: str,
    attempt_dir: Path,
    provider: str,
    package_version: str,
    rounds: int,
    timeout: int,
    profile: str = "lean",
) -> dict[str, Any]:
    attempt_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "uvx",
        "--python",
        "3.12",
        "--from",
        f"autocontext=={package_version}",
        "autoctx",
        "improve",
        "--task-prompt",
        prompt,
        "--rubric",
        rubric,
        "--output",
        fenced(current_proof),
        "--rounds",
        str(rounds),
        "--threshold",
        "0.99",
        "--provider",
        provider,
        "--timeout",
        str(timeout),
        "--json",
    ]
    env = os.environ.copy()
    env.pop("UV_EXCLUDE_NEWER", None)
    env.update(
        {
            "AUTOCONTEXT_AGENT_PROVIDER": provider,
            "AUTOCONTEXT_JUDGE_PROVIDER": provider,
            "AUTOCONTEXT_PI_COMMAND": "pi",
            "AUTOCONTEXT_PI_NO_CONTEXT_FILES": "1",
            "AUTOCONTEXT_PI_TIMEOUT": str(timeout),
            "AUTOCONTEXT_HARNESS_PROFILE": profile,
        }
    )
    (attempt_dir / "repair_prompt.md").write_text(prompt, encoding="utf-8")
    (attempt_dir / "repair_rubric.md").write_text(rubric, encoding="utf-8")
    (attempt_dir / "autoctx_command.json").write_text(
        json.dumps(cmd, indent=2), encoding="utf-8"
    )
    started = time.time()
    deadline = max(timeout * (rounds + 2), timeout + 60)
    proc = popen_process_group(cmd, cwd=attempt_dir, env=env)
    stdout, stderr, timed_out, exit_code = communicate_process_group(
        proc,
        timeout=deadline,
        timeout_marker=f"EXTERNAL_TIMEOUT after {deadline}s",
    )
    elapsed = round(time.time() - started, 2)
    (attempt_dir / "autoctx_stdout.log").write_text(stdout, encoding="utf-8")
    (attempt_dir / "autoctx_stderr.log").write_text(stderr, encoding="utf-8")
    extracted = extract(stdout)
    edit_from_current = (
        proof_edit_metrics(current_proof, extracted) if extracted else None
    )
    result = {
        "exit_code": exit_code,
        "timed_out": timed_out,
        "elapsed_seconds": elapsed,
        "extracted_proof": extracted,
        "extracted_proof_features": proof_features(extracted),
        "extracted_proof_feature_summary": proof_feature_summary(extracted),
        "edit_from_current": edit_from_current,
        "edit_from_current_summary": proof_edit_summary_text(edit_from_current),
    }
    try:
        start = stdout.find("{")
        if start >= 0:
            result["json"] = json.loads(stdout[start:])
    except Exception as exc:  # noqa: BLE001
        result["json_parse_error"] = str(exc)
    (attempt_dir / "autoctx_result.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", default="double_eq_two_mul")
    parser.add_argument("--initial-proof", default="rfl")
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=5,
        help="Maximum Lean verifications, including the initial proof",
    )
    parser.add_argument(
        "--rounds", type=int, default=2, help="autoctx improve rounds per repair step"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="CLI-backed provider timeout for each repair call",
    )
    parser.add_argument("--provider", default="pi")
    parser.add_argument("--package-version", default="0.5.1")
    parser.add_argument(
        "--run-dir",
        help="Optional explicit output directory for batch experiments",
    )
    parser.add_argument(
        "--mathlib-index",
        default=os.environ.get(mathlib_retrieval.INDEX_ENV_VAR, ""),
        help=(
            "Path to a Mathlib declaration index JSON (dump of the pinned "
            "revision). When set, enables the lean-mathlib profile: retrieved "
            "candidate lemmas are injected into the repair prompt and Mathlib "
            "imports are permitted. Defaults to $AUTOCONTEXT_MATHLIB_INDEX."
        ),
    )
    args = parser.parse_args()

    mathlib_index = mathlib_retrieval.load_index(args.mathlib_index or None)
    allow_mathlib = bool(mathlib_index)
    harness_profile = "lean-mathlib" if allow_mathlib else "lean"

    run_dir = (
        Path(args.run_dir)
        if args.run_dir
        else ROOT / "results" / f"{utc_stamp()}_{args.fixture}_loop"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "fixture": args.fixture,
        "run_dir": str(run_dir),
        "provider": args.provider,
        "package_version": args.package_version,
        "max_attempts": args.max_attempts,
        "rounds_per_repair": args.rounds,
        "harness_profile": harness_profile,
        "mathlib_index_size": len(mathlib_index),
        "proved": False,
        "attempts": [],
    }

    proof = args.initial_proof
    history: list[dict[str, Any]] = []
    rubric = build_rubric()

    for attempt in range(args.max_attempts):
        attempt_dir = run_dir / f"attempt_{attempt:02d}"
        verification = verify_attempt(
            fixture=args.fixture,
            proof=proof,
            attempt_dir=attempt_dir,
        )
        attempt_summary = {
            "attempt": attempt,
            "proof": proof,
            "proof_features": proof_features(proof),
            "proof_feature_summary": proof_feature_summary(proof),
            "ok": bool(verification.get("ok")),
            "verification": verification,
        }
        summary["attempts"].append(attempt_summary)
        history.append(history_item(attempt, proof, bool(verification.get("ok"))))
        (run_dir / "summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        print(
            json.dumps(
                {"event": "verified", "attempt": attempt, "ok": verification.get("ok")}
            ),
            flush=True,
        )
        if verification.get("ok"):
            summary["proved"] = True
            summary["final_proof"] = proof
            summary["final_proof_features"] = proof_features(proof)
            summary["final_proof_feature_summary"] = proof_feature_summary(proof)
            summary["final_attempt"] = attempt
            summary["proof_edit_summary"] = proof_edit_summary_from_attempts(summary)
            (run_dir / "summary.json").write_text(
                json.dumps(summary, indent=2), encoding="utf-8"
            )
            print(json.dumps(summary, indent=2))
            return 0
        if attempt == args.max_attempts - 1:
            break

        lemma_block = ""
        if allow_mathlib:
            lemma_block = mathlib_retrieval.lemma_block_for(
                template=load_template(args.fixture),
                feedback=concise_verifier_feedback(verification),
                index=mathlib_index,
            )
            attempt_summary["retrieved_lemma_block"] = lemma_block
        repair_prompt = build_repair_prompt(
            fixture=args.fixture,
            proof=proof,
            verification=verification,
            attempt_index=attempt,
            history=history,
            lemma_block=lemma_block,
            allow_mathlib=allow_mathlib,
        )
        repair = run_autoctx_repair(
            prompt=repair_prompt,
            rubric=rubric,
            current_proof=proof,
            attempt_dir=attempt_dir,
            provider=args.provider,
            package_version=args.package_version,
            rounds=args.rounds,
            timeout=args.timeout,
            profile=harness_profile,
        )
        attempt_summary["repair"] = repair
        next_proof = str(repair.get("extracted_proof") or "").strip()
        if next_proof:
            attempt_summary["proof_edit"] = proof_edit_metrics(proof, next_proof)
            attempt_summary["proof_edit_summary"] = proof_edit_summary_text(
                attempt_summary["proof_edit"]
            )
        proof = next_proof or proof

    summary["proved"] = False
    summary["final_proof"] = proof
    summary["final_proof_features"] = proof_features(proof)
    summary["final_proof_feature_summary"] = proof_feature_summary(proof)
    summary["proof_edit_summary"] = proof_edit_summary_from_attempts(summary)
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
