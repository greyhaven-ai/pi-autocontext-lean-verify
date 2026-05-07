"""Shared helpers for the external Lean/autocontext/Pi experiment scripts."""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verify_lean_proof import verify

ROOT = Path(__file__).resolve().parent

PROOF_TACTIC_FEATURES = [
    "induction",
    "simp",
    "rw",
    "omega",
    "rfl",
    "exact",
    "cases",
    "constructor",
    "congrArg",
]

PRIORITY_LEMMA_FEATURES = [
    "Nat.mul_succ",
    "Nat.mul_add",
    "Nat.add_assoc",
    "Nat.add_comm",
    "Nat.add_left_comm",
    "Nat.succ_eq_add_one",
    "Nat.succ_add",
    "Nat.add_succ",
]

INDEXED_PROOF_FEATURES = [
    "induction",
    "simp",
    "rw",
    "omega",
    "Nat.mul_succ",
    "Nat.mul_add",
    "Nat.add_assoc",
    "Nat.add_comm",
    "Nat.add_left_comm",
    "Nat.succ_eq_add_one",
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _feature_key(name: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z]+", "_", name).strip("_").lower()
    return f"uses_{normalized}"


def _ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _token_count(text: str, token: str) -> int:
    if "." in token:
        return len(
            re.findall(rf"(?<![A-Za-z0-9_'.]){re.escape(token)}(?![A-Za-z0-9_'])", text)
        )
    return len(
        re.findall(rf"(?<![A-Za-z0-9_'.]){re.escape(token)}(?![A-Za-z0-9_'])", text)
    )


def proof_features(proof: object) -> dict[str, Any]:
    """Return derived lemma/tactic features for a Lean proof body.

    These metrics are reporting aids only. Lean verification remains the source of
    truth for correctness.
    """

    text = str(proof or "")
    named_lemmas = _ordered_unique(
        re.findall(r"\b(?:Nat|List|Bool)\.[A-Za-z_][A-Za-z0-9_']*\b", text)
    )
    tactic_counts = {
        tactic: _token_count(text, tactic) for tactic in PROOF_TACTIC_FEATURES
    }
    lemma_counts = {lemma: _token_count(text, lemma) for lemma in named_lemmas}
    counts = {
        feature: count
        for feature, count in {**tactic_counts, **lemma_counts}.items()
        if count
    }
    tactics = [tactic for tactic in PROOF_TACTIC_FEATURES if tactic_counts[tactic]]
    lemmas = [lemma for lemma in named_lemmas if lemma_counts.get(lemma)]
    features: dict[str, Any] = {
        "lemmas": lemmas,
        "tactics": tactics,
        "counts": counts,
    }
    for feature in PROOF_TACTIC_FEATURES + _ordered_unique(
        PRIORITY_LEMMA_FEATURES + lemmas
    ):
        features[_feature_key(feature)] = bool(counts.get(feature))
    return features


def proof_feature_summary(features_or_proof: object, limit: int = 8) -> str:
    features = (
        features_or_proof
        if isinstance(features_or_proof, dict)
        and ("lemmas" in features_or_proof or "tactics" in features_or_proof)
        else proof_features(features_or_proof)
    )
    selected = _ordered_unique(
        list(features.get("tactics") or [])
        + [
            lemma
            for lemma in PRIORITY_LEMMA_FEATURES
            if lemma in features.get("lemmas", [])
        ]
        + list(features.get("lemmas") or [])
    )
    if not selected:
        return "none"
    shown = selected[:limit]
    suffix = f", +{len(selected) - limit} more" if len(selected) > limit else ""
    return ", ".join(shown) + suffix


def aggregate_feature_usage(
    rows: list[dict[str, Any]], *, only_proved: bool = True
) -> dict[str, int]:
    usage: dict[str, int] = {}
    for row in rows:
        if only_proved and not row.get("proved"):
            continue
        features = row.get("proof_features") or proof_features(row.get("final_proof"))
        for feature in INDEXED_PROOF_FEATURES:
            if features.get(_feature_key(feature)):
                usage[feature] = usage.get(feature, 0) + 1
    return usage


def _proof_tokens(proof: object) -> list[str]:
    return re.findall(r"[A-Za-z_][A-Za-z0-9_'.]*|[0-9]+|[^\s]", str(proof or ""))


def _proof_lines(proof: object) -> list[str]:
    return [line.rstrip() for line in str(proof or "").strip().splitlines()]


def _levenshtein(left: list[str], right: list[str]) -> int:
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for left_index, left_item in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_item in enumerate(right, start=1):
            cost = 0 if left_item == right_item else 1
            current.append(
                min(
                    previous[right_index] + 1,
                    current[right_index - 1] + 1,
                    previous[right_index - 1] + cost,
                )
            )
        previous = current
    return previous[-1]


def _normalized_distance(distance: int, left_len: int, right_len: int) -> float:
    denominator = max(left_len, right_len, 1)
    return round(distance / denominator, 4)


def _similarity(left: list[str], right: list[str]) -> float:
    return round(SequenceMatcher(a=left, b=right, autojunk=False).ratio(), 4)


def _present_indexed_features(features: dict[str, Any]) -> list[str]:
    return [
        feature
        for feature in INDEXED_PROOF_FEATURES
        if features.get(_feature_key(feature))
    ]


def proof_edit_metrics(before: object, after: object) -> dict[str, Any]:
    """Measure how much a proof changed between two candidate bodies.

    Distances are reporting metrics only; they do not imply semantic proof quality.
    """

    before_text = str(before or "")
    after_text = str(after or "")
    before_chars = list(before_text)
    after_chars = list(after_text)
    before_tokens = _proof_tokens(before_text)
    after_tokens = _proof_tokens(after_text)
    before_lines = _proof_lines(before_text)
    after_lines = _proof_lines(after_text)
    char_distance = _levenshtein(before_chars, after_chars)
    token_distance = _levenshtein(before_tokens, after_tokens)
    line_distance = _levenshtein(before_lines, after_lines)
    before_features = proof_features(before_text)
    after_features = proof_features(after_text)
    before_feature_set = set(_present_indexed_features(before_features))
    after_feature_set = set(_present_indexed_features(after_features))
    return {
        "char_distance": char_distance,
        "token_distance": token_distance,
        "line_distance": line_distance,
        "char_distance_ratio": _normalized_distance(
            char_distance, len(before_chars), len(after_chars)
        ),
        "token_distance_ratio": _normalized_distance(
            token_distance, len(before_tokens), len(after_tokens)
        ),
        "line_distance_ratio": _normalized_distance(
            line_distance, len(before_lines), len(after_lines)
        ),
        "char_similarity": _similarity(before_chars, after_chars),
        "token_similarity": _similarity(before_tokens, after_tokens),
        "line_similarity": _similarity(before_lines, after_lines),
        "before_chars": len(before_chars),
        "after_chars": len(after_chars),
        "before_tokens": len(before_tokens),
        "after_tokens": len(after_tokens),
        "before_lines": len(before_lines),
        "after_lines": len(after_lines),
        "delta_chars": len(after_chars) - len(before_chars),
        "delta_tokens": len(after_tokens) - len(before_tokens),
        "delta_lines": len(after_lines) - len(before_lines),
        "gained_features": sorted(after_feature_set - before_feature_set),
        "lost_features": sorted(before_feature_set - after_feature_set),
    }


def proof_edit_summary_text(metrics: dict[str, Any] | None) -> str:
    if not metrics:
        return "none"
    parts = [
        f"tok={metrics.get('token_distance')}",
        f"line={metrics.get('line_distance')}",
        f"sim={metrics.get('token_similarity')}",
    ]
    gained = metrics.get("gained_features") or []
    if gained:
        parts.append("+" + "+".join(gained[:4]))
    return ", ".join(parts)


def _repair_result_from_attempt(attempt: dict[str, Any]) -> dict[str, Any] | None:
    return attempt.get("repair")


def attempt_edit_metrics(attempt: dict[str, Any]) -> dict[str, Any] | None:
    if attempt.get("proof_edit"):
        return attempt["proof_edit"]
    repair = _repair_result_from_attempt(attempt)
    if not repair:
        return None
    after = str(repair.get("extracted_proof") or "").strip()
    if not after:
        return None
    return proof_edit_metrics(attempt.get("proof"), after)


def proof_edit_summary_from_attempts(summary: dict[str, Any]) -> dict[str, Any]:
    attempts = list(summary.get("attempts") or [])
    edits = [edit for attempt in attempts if (edit := attempt_edit_metrics(attempt))]
    initial_proof = attempts[0].get("proof") if attempts else None
    final_proof = summary.get("final_proof")
    final_edit = (
        proof_edit_metrics(initial_proof, final_proof)
        if initial_proof is not None and final_proof is not None
        else None
    )
    if not edits:
        return {
            "repair_edits": 0,
            "total_token_distance": 0,
            "max_token_distance": 0,
            "mean_token_distance": 0,
            "total_line_distance": 0,
            "max_line_distance": 0,
            "mean_line_distance": 0,
            "final_from_initial": final_edit,
        }
    total_tokens = sum(int(edit.get("token_distance") or 0) for edit in edits)
    total_lines = sum(int(edit.get("line_distance") or 0) for edit in edits)
    gained: dict[str, int] = {}
    for edit in edits:
        for feature in edit.get("gained_features") or []:
            gained[feature] = gained.get(feature, 0) + 1
    return {
        "repair_edits": len(edits),
        "total_token_distance": total_tokens,
        "max_token_distance": max(
            int(edit.get("token_distance") or 0) for edit in edits
        ),
        "mean_token_distance": round(total_tokens / len(edits), 2),
        "total_line_distance": total_lines,
        "max_line_distance": max(int(edit.get("line_distance") or 0) for edit in edits),
        "mean_line_distance": round(total_lines / len(edits), 2),
        "gained_feature_counts": gained,
        "final_from_initial": final_edit,
    }


def _load_summary_for_row(row: dict[str, Any]) -> dict[str, Any] | None:
    summary_path = row.get("summary_path")
    if not summary_path:
        return None
    path = Path(str(summary_path))
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def row_proof_edit_summary(row: dict[str, Any]) -> dict[str, Any]:
    if row.get("proof_edit_summary"):
        return row["proof_edit_summary"]
    summary = _load_summary_for_row(row)
    if summary:
        return summary.get("proof_edit_summary") or proof_edit_summary_from_attempts(
            summary
        )
    return proof_edit_summary_from_attempts(
        {"attempts": [], "final_proof": row.get("final_proof")}
    )


def aggregate_proof_edit_usage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summaries = [row_proof_edit_summary(row) for row in rows]
    if not summaries:
        return {
            "rows": 0,
            "repair_edits": 0,
            "total_token_distance": 0,
            "mean_token_distance_per_row": 0,
            "mean_token_distance_per_edit": 0,
        }
    repair_edits = sum(int(summary.get("repair_edits") or 0) for summary in summaries)
    total_tokens = sum(
        int(summary.get("total_token_distance") or 0) for summary in summaries
    )
    total_lines = sum(
        int(summary.get("total_line_distance") or 0) for summary in summaries
    )
    gained: dict[str, int] = {}
    for summary in summaries:
        for feature, count in (summary.get("gained_feature_counts") or {}).items():
            gained[feature] = gained.get(feature, 0) + int(count)
    return {
        "rows": len(summaries),
        "repair_edits": repair_edits,
        "total_token_distance": total_tokens,
        "total_line_distance": total_lines,
        "mean_token_distance_per_row": round(total_tokens / len(summaries), 2),
        "mean_line_distance_per_row": round(total_lines / len(summaries), 2),
        "mean_token_distance_per_edit": round(total_tokens / repair_edits, 2)
        if repair_edits
        else 0,
        "mean_line_distance_per_edit": round(total_lines / repair_edits, 2)
        if repair_edits
        else 0,
        "gained_feature_counts": gained,
    }


def load_template(fixture: str) -> str:
    return (ROOT / "fixtures" / fixture / "Theorem.template.lean").read_text(
        encoding="utf-8"
    )


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_fixtures(
    manifest: dict[str, Any],
    requested: list[str] | None,
    max_fixtures: int | None = None,
) -> list[dict[str, Any]]:
    fixtures = list(manifest["fixtures"])
    if requested:
        by_id = {fixture["id"]: fixture for fixture in fixtures}
        missing = [fixture_id for fixture_id in requested if fixture_id not in by_id]
        if missing:
            raise SystemExit(f"Unknown fixture(s): {', '.join(missing)}")
        fixtures = [by_id[fixture_id] for fixture_id in requested]
    if max_fixtures is not None:
        fixtures = fixtures[:max_fixtures]
    return fixtures


def resolve_run_root(explicit: str | None, suffix: str) -> Path:
    return Path(explicit) if explicit else ROOT / "results" / f"{utc_stamp()}_{suffix}"


def attempt_tool_calls(summary: dict[str, Any]) -> int:
    return sum(
        1
        for attempt in summary.get("attempts", [])
        if "pi" in attempt or "repair" in attempt
    )


def autocontext_repair_calls(summary: dict[str, Any]) -> int:
    return sum(1 for attempt in summary.get("attempts", []) if "repair" in attempt)


def proof_preview(proof: object, limit: int = 220) -> str:
    text = str(proof or "").replace("\n", "<br>")
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text.replace("`", "'")


def direct_pi_command(
    *,
    fixture_id: str,
    mode: str,
    initial_proof: str,
    max_attempts: int,
    timeout: int,
    run_dir: Path,
    pi_provider: str | None = None,
    pi_model: str | None = None,
    thinking: str | None = None,
) -> list[str]:
    cmd = [
        str(ROOT / "direct_pi_prove.py"),
        "--fixture",
        fixture_id,
        "--mode",
        mode,
        "--initial-proof",
        initial_proof,
        "--max-attempts",
        str(max_attempts),
        "--timeout",
        str(timeout),
        "--run-dir",
        str(run_dir),
    ]
    if pi_provider:
        cmd.extend(["--pi-provider", pi_provider])
    if pi_model:
        cmd.extend(["--pi-model", pi_model])
    if thinking:
        cmd.extend(["--thinking", thinking])
    return cmd


def concise_verifier_feedback(result: dict[str, Any]) -> str:
    parts: list[str] = []
    if result.get("error"):
        parts.append(f"Verifier error: {result['error']}")
    if result.get("forbidden_patterns"):
        parts.append(f"Forbidden patterns: {result['forbidden_patterns']}")
    stdout = str(result.get("stdout") or "").strip()
    stderr = str(result.get("stderr") or "").strip()
    if stdout:
        parts.append(f"Lean stdout:\n{stdout[-4000:]}")
    if stderr:
        parts.append(f"Lean stderr:\n{stderr[-4000:]}")
    if not parts:
        parts.append(json.dumps(result, indent=2)[-4000:])
    return "\n\n".join(parts)


def history_summary(history: list[dict[str, Any]], limit: int = 4) -> str:
    return (
        "\n".join(
            f"- attempt {item['attempt']}: ok={item['ok']} proof={item['proof_preview']!r}"
            for item in history[-limit:]
        )
        or "- none yet"
    )


def history_item(attempt: int, proof: str, ok: bool) -> dict[str, Any]:
    return {
        "attempt": attempt,
        "ok": ok,
        "proof_preview": proof.strip().replace("\n", " ")[:160],
    }


def verify_attempt(*, fixture: str, proof: str, attempt_dir: Path) -> dict[str, Any]:
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "candidate_proof.lean").write_text(
        proof.strip() + "\n", encoding="utf-8"
    )
    verification = verify(
        fixture=fixture,
        proof_text=proof,
        work_dir=attempt_dir / "verify",
    )
    (attempt_dir / "lean_result.json").write_text(
        json.dumps(verification, indent=2), encoding="utf-8"
    )
    return verification
