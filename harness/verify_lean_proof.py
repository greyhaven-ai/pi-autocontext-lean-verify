#!/usr/bin/env python3
"""Verify a candidate Lean proof body against a fixed theorem template.

The candidate supplies only the proof body after `:= by`; the theorem statement and
supporting definitions come from the fixture template. This prevents theorem
weakening and keeps the final acceptance criterion machine-checkable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_LEAN = Path("/tmp/autocontext-elan-home/bin/lean")
FORBIDDEN_PATTERNS = [
    r"\bsorry\b",
    r"\badmit\b",
    r"\baxiom\b",
    r"\bunsafe\b",
    r"\bset_option\s+autoImplicit\s+true\b",
]


def _strip_line_comments(text: str) -> str:
    return "\n".join(line.split("--", 1)[0] for line in text.splitlines())


def _lean_bin() -> str | None:
    env = os.getenv("LEAN_BIN")
    if env:
        return env
    if DEFAULT_LEAN.exists():
        return str(DEFAULT_LEAN)
    return shutil.which("lean")


def _lean_env() -> dict[str, str]:
    env = os.environ.copy()
    if DEFAULT_LEAN.exists() and "ELAN_HOME" not in env:
        env["ELAN_HOME"] = str(DEFAULT_LEAN.parent.parent)
    return env


def _indent_proof(text: str) -> str:
    lines = text.strip("\n").splitlines()
    if not lines:
        return "  -- empty candidate proof"
    # Strip fenced-code wrappers if a raw block was passed by accident.
    if lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(f"  {line}" if line.strip() else "" for line in lines)


def _forbidden_hits(proof: str) -> list[str]:
    scan = _strip_line_comments(proof)
    return [
        pattern
        for pattern in FORBIDDEN_PATTERNS
        if re.search(pattern, scan, flags=re.IGNORECASE)
    ]


def verify(
    *, fixture: str, proof_text: str, work_dir: Path | None = None
) -> dict[str, object]:
    fixture_dir = ROOT / "fixtures" / fixture
    template_path = fixture_dir / "Theorem.template.lean"
    if not template_path.exists():
        return {
            "ok": False,
            "error": f"unknown fixture {fixture!r}",
            "fixture_dir": str(fixture_dir),
        }

    hits = _forbidden_hits(proof_text)
    if hits:
        return {
            "ok": False,
            "error": "forbidden proof token",
            "forbidden_patterns": hits,
        }

    lean = _lean_bin()
    if not lean:
        return {
            "ok": False,
            "error": "Lean executable not found",
            "install_hint": "Run: ELAN_HOME=/tmp/autocontext-elan-home sh elan-init.sh -y --default-toolchain stable --no-modify-path",
        }

    theorem = template_path.read_text(encoding="utf-8").replace(
        "{{PROOF}}", _indent_proof(proof_text)
    )
    if work_dir is None:
        temp = tempfile.TemporaryDirectory(prefix="autocontext-lean-proof-")
        candidate_dir = Path(temp.name)
    else:
        temp = None
        candidate_dir = work_dir
        candidate_dir.mkdir(parents=True, exist_ok=True)

    candidate_path = candidate_dir / "Candidate.lean"
    candidate_path.write_text(theorem, encoding="utf-8")

    try:
        proc = subprocess.run(
            [lean, str(candidate_path)],
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
            env=_lean_env(),
        )
    except subprocess.TimeoutExpired:
        result = {
            "ok": False,
            "error": "lean verifier timeout",
            "candidate_path": str(candidate_path),
        }
    else:
        stderr_lower = proc.stderr.lower()
        sorry_warning = (
            "declaration uses 'sorry'" in stderr_lower
            or "contains sorry" in stderr_lower
        )
        result = {
            "ok": proc.returncode == 0 and not sorry_warning,
            "exit_code": proc.returncode,
            "candidate_path": str(candidate_path),
            "lean": lean,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "sorry_warning": sorry_warning,
        }
    finally:
        if temp is not None:
            # Keep failed candidates would be useful, but this function is also used in tight loops.
            temp.cleanup()

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="Fixture name under fixtures/")
    parser.add_argument("--proof-file", help="Path containing candidate proof body")
    parser.add_argument("--proof-text", help="Candidate proof body")
    parser.add_argument("--work-dir", help="Directory to write Candidate.lean into")
    args = parser.parse_args()

    if args.proof_text is None and args.proof_file is None:
        proof_text = sys.stdin.read()
    elif args.proof_text is not None:
        proof_text = args.proof_text
    else:
        proof_text = Path(args.proof_file).read_text(encoding="utf-8")

    result = verify(
        fixture=args.fixture,
        proof_text=proof_text,
        work_dir=Path(args.work_dir) if args.work_dir else None,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
