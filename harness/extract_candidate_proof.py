#!/usr/bin/env python3
"""Extract a Lean proof body from autocontext/Pi output.

Accepts raw text or JSON. Prefer fenced Lean code blocks; otherwise falls back to
common JSON fields and then the whole text.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

CODE_BLOCK_RE = re.compile(
    r"```(?:lean|lean4)?\s*\n(?P<code>.*?)```", re.IGNORECASE | re.DOTALL
)


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        preferred = [
            "final_output",
            "output",
            "text",
            "best_output",
            "best_strategy",
            "proof",
            "lean_code",
            "result",
        ]
        for key in preferred:
            if key in value:
                out.extend(_walk_strings(value[key]))
        for key, nested in value.items():
            if key not in preferred:
                out.extend(_walk_strings(nested))
        return out
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(_walk_strings(item))
        return out
    return []


def normalize_proof_body(candidate: str) -> str:
    """Return a proof body even if the model emitted a whole theorem block."""
    candidate = candidate.strip()
    theorem_match = re.search(
        r"\btheorem\b[\s\S]*?:=\s*by\s*\n(?P<body>[\s\S]*)", candidate
    )
    if theorem_match:
        return textwrap.dedent(theorem_match.group("body")).strip()
    return candidate


def extract(text: str) -> str:
    candidates: list[str] = []
    try:
        parsed = json.loads(text[text.find("{") :]) if "{" in text else None
    except Exception:
        parsed = None
    if parsed is not None:
        candidates.extend(_walk_strings(parsed))
    candidates.append(text)

    for candidate in candidates:
        match = CODE_BLOCK_RE.search(candidate)
        if match:
            return normalize_proof_body(match.group("code"))

    # Fall back to lines after common labels.
    for candidate in candidates:
        marker_match = re.search(
            r"(?:proof body|lean proof|proof)\s*:\s*\n(?P<body>.+)",
            candidate,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if marker_match:
            return normalize_proof_body(marker_match.group("body"))

    return normalize_proof_body(candidates[0]) if candidates else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Input file, defaults to stdin")
    parser.add_argument("--output", "-o", help="Write extracted proof to this file")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    )
    proof = extract(text)
    if args.output:
        Path(args.output).write_text(proof + "\n", encoding="utf-8")
    else:
        print(proof)
    return 0 if proof else 1


if __name__ == "__main__":
    raise SystemExit(main())
