#!/usr/bin/env python3
"""Direct Pi baselines for the Lean proof experiment.

Modes:
- one-shot: ask Pi once for a proof body, then verify with Lean.
- repair-loop: start from an initial proof, feed Lean errors directly to Pi, and verify each repair.

This intentionally bypasses autocontext so it can be compared against the
`prove_with_autocontext.py` experiment loop.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
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
from extract_candidate_proof import extract

SYSTEM_PROMPT = """You are a Lean 4 theorem-proving assistant.
Return only a proof body that can replace a `{{PROOF}}` placeholder after `:= by`.
Do not use sorry, admit, axiom, unsafe, new imports, or modified theorem statements.
Prefer one fenced Lean code block with no prose outside it.
"""


def build_one_shot_prompt(fixture: str) -> str:
    return f"""Produce a Lean 4 proof body for the fixed theorem below.

Rules:
- Output ONLY the proof body for `{{PROOF}}`, preferably in one fenced Lean block.
- Do not output a modified theorem statement.
- Do not use `sorry`, `admit`, `axiom`, `unsafe`, or new imports.
- Use only Lean core/Init facts available in Lean 4 stable. No Mathlib imports.

Fixed theorem template:
```lean
{load_template(fixture)}
```
"""


def build_repair_prompt(
    *,
    fixture: str,
    proof: str,
    verification: dict[str, Any],
    attempt_index: int,
    history: list[dict[str, Any]],
) -> str:
    history_text = history_summary(history)
    return f"""Repair this Lean 4 proof body using the real Lean verifier feedback.

You are not allowed to change the theorem template. Output only a corrected proof body for the `{{PROOF}}` placeholder.

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

Recent attempt history:
{history_text}

Rules:
- Output ONLY the proof body, preferably in one fenced Lean code block.
- Do not include prose outside the code block.
- Do not use `sorry`, `admit`, `axiom`, `unsafe`, new imports, or a modified theorem statement.
- Use Lean core/Init facts only; no Mathlib imports.
- If the error says a tactic failed, choose a different Lean proof strategy.
"""


def pi_command(args: argparse.Namespace, prompt: str) -> list[str]:
    cmd = [
        "pi",
        "--print",
        "--no-session",
        "--no-context-files",
        "--no-tools",
        "--no-skills",
        "--no-prompt-templates",
        "--no-themes",
        "--mode",
        "text",
        "--system-prompt",
        SYSTEM_PROMPT,
    ]
    if args.pi_provider:
        cmd.extend(["--provider", args.pi_provider])
    if args.pi_model:
        cmd.extend(["--model", args.pi_model])
    if args.thinking:
        cmd.extend(["--thinking", args.thinking])
    cmd.append(prompt)
    return cmd


def run_pi(
    *, prompt: str, attempt_dir: Path, args: argparse.Namespace, label: str
) -> dict[str, Any]:
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / f"{label}_prompt.md").write_text(prompt, encoding="utf-8")
    cmd = pi_command(args, prompt)
    redacted_cmd = ["<PROMPT>" if item == prompt else item for item in cmd]
    (attempt_dir / f"{label}_pi_command.json").write_text(
        json.dumps(redacted_cmd, indent=2), encoding="utf-8"
    )
    env = os.environ.copy()
    env.update({"PI_OFFLINE": "1"})
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=attempt_dir,
            text=True,
            capture_output=True,
            timeout=args.timeout,
            check=False,
            env=env,
        )
        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = (
            exc.stdout
            if isinstance(exc.stdout, str)
            else (exc.stdout or b"").decode(errors="replace")
        )
        stderr = (
            exc.stderr
            if isinstance(exc.stderr, str)
            else (exc.stderr or b"").decode(errors="replace")
        )
        stderr += "\nDIRECT_PI_TIMEOUT\n"
        exit_code = 124
        timed_out = True
    elapsed = round(time.time() - started, 2)
    (attempt_dir / f"{label}_pi_stdout.log").write_text(stdout, encoding="utf-8")
    (attempt_dir / f"{label}_pi_stderr.log").write_text(stderr, encoding="utf-8")
    proof = extract(stdout)
    result = {
        "exit_code": exit_code,
        "timed_out": timed_out,
        "elapsed_seconds": elapsed,
        "extracted_proof": proof,
        "extracted_proof_features": proof_features(proof),
        "extracted_proof_feature_summary": proof_feature_summary(proof),
    }
    (attempt_dir / f"{label}_pi_result.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


def run_one_shot(args: argparse.Namespace, run_dir: Path) -> dict[str, Any]:
    attempt_dir = run_dir / "attempt_00"
    prompt = build_one_shot_prompt(args.fixture)
    pi_result = run_pi(
        prompt=prompt, attempt_dir=attempt_dir, args=args, label="oneshot"
    )
    proof = str(pi_result.get("extracted_proof") or "").strip()
    verification = verify_attempt(
        fixture=args.fixture,
        proof=proof,
        attempt_dir=attempt_dir,
    )
    summary = {
        "mode": "one-shot",
        "fixture": args.fixture,
        "run_dir": str(run_dir),
        "provider": "direct-pi",
        "pi_provider": args.pi_provider,
        "pi_model": args.pi_model,
        "proved": bool(verification.get("ok")),
        "final_attempt": 0 if verification.get("ok") else None,
        "final_proof": proof,
        "final_proof_features": proof_features(proof),
        "final_proof_feature_summary": proof_feature_summary(proof),
        "attempts": [
            {
                "attempt": 0,
                "proof": proof,
                "proof_features": proof_features(proof),
                "proof_feature_summary": proof_feature_summary(proof),
                "ok": bool(verification.get("ok")),
                "pi": pi_result,
                "verification": verification,
            }
        ],
    }
    summary["proof_edit_summary"] = proof_edit_summary_from_attempts(summary)
    return summary


def run_repair_loop(args: argparse.Namespace, run_dir: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "mode": "repair-loop",
        "fixture": args.fixture,
        "run_dir": str(run_dir),
        "provider": "direct-pi",
        "pi_provider": args.pi_provider,
        "pi_model": args.pi_model,
        "max_attempts": args.max_attempts,
        "proved": False,
        "attempts": [],
    }
    proof = args.initial_proof
    history: list[dict[str, Any]] = []
    for attempt in range(args.max_attempts):
        attempt_dir = run_dir / f"attempt_{attempt:02d}"
        verification = verify_attempt(
            fixture=args.fixture,
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
        summary["attempts"].append(attempt_summary)
        history.append(history_item(attempt, proof, bool(verification.get("ok"))))
        print(
            json.dumps(
                {"event": "verified", "attempt": attempt, "ok": verification.get("ok")}
            ),
            flush=True,
        )
        if verification.get("ok"):
            summary["proved"] = True
            summary["final_attempt"] = attempt
            summary["final_proof"] = proof
            summary["final_proof_features"] = proof_features(proof)
            summary["final_proof_feature_summary"] = proof_feature_summary(proof)
            summary["proof_edit_summary"] = proof_edit_summary_from_attempts(summary)
            return summary
        if attempt == args.max_attempts - 1:
            break
        prompt = build_repair_prompt(
            fixture=args.fixture,
            proof=proof,
            verification=verification,
            attempt_index=attempt,
            history=history,
        )
        pi_result = run_pi(
            prompt=prompt, attempt_dir=attempt_dir, args=args, label="repair"
        )
        attempt_summary["repair"] = pi_result
        next_proof = str(pi_result.get("extracted_proof") or "").strip()
        if next_proof:
            attempt_summary["proof_edit"] = proof_edit_metrics(proof, next_proof)
            attempt_summary["proof_edit_summary"] = proof_edit_summary_text(
                attempt_summary["proof_edit"]
            )
        proof = next_proof or proof
    summary["final_proof"] = proof
    summary["final_proof_features"] = proof_features(proof)
    summary["final_proof_feature_summary"] = proof_feature_summary(proof)
    summary["proof_edit_summary"] = proof_edit_summary_from_attempts(summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", default="double_eq_two_mul")
    parser.add_argument(
        "--mode", choices=["one-shot", "repair-loop"], default="repair-loop"
    )
    parser.add_argument("--initial-proof", default="rfl")
    parser.add_argument("--max-attempts", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument(
        "--pi-provider", help="Optional provider passed to pi --provider"
    )
    parser.add_argument("--pi-model", help="Optional model passed to pi --model")
    parser.add_argument(
        "--thinking", help="Optional thinking level passed to pi --thinking"
    )
    parser.add_argument("--run-dir", help="Optional explicit output directory")
    args = parser.parse_args()

    run_dir = (
        Path(args.run_dir)
        if args.run_dir
        else ROOT / "results" / f"{utc_stamp()}_{args.fixture}_direct_pi_{args.mode}"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "one-shot":
        summary = run_one_shot(args, run_dir)
    else:
        summary = run_repair_loop(args, run_dir)
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0 if summary.get("proved") else 1


if __name__ == "__main__":
    raise SystemExit(main())
