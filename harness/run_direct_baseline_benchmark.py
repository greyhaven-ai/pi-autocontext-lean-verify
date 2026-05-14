#!/usr/bin/env python3
"""Run direct-Pi one-shot and repair-loop baselines across Lean fixtures."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from process_utils import communicate_process_group, popen_process_group

from experiment_common import (
    ROOT,
    aggregate_feature_usage,
    aggregate_proof_edit_usage,
    attempt_tool_calls,
    direct_pi_command,
    load_manifest,
    proof_edit_summary_from_attempts,
    proof_feature_summary,
    proof_features,
    proof_preview,
    resolve_run_root,
    selected_fixtures,
)


def run_case(
    *,
    fixture: dict[str, Any],
    mode: str,
    run_root: Path,
    args: argparse.Namespace,
) -> dict[str, Any]:
    fixture_id = fixture["id"]
    case_dir = run_root / mode / fixture_id
    cmd = direct_pi_command(
        fixture_id=fixture_id,
        mode=mode,
        initial_proof=fixture.get("initial_proof", "rfl"),
        max_attempts=args.max_attempts,
        timeout=args.timeout,
        run_dir=case_dir,
        pi_provider=args.pi_provider,
        pi_model=args.pi_model,
        thinking=args.thinking,
    )

    started = time.time()
    proc = popen_process_group(cmd, cwd=ROOT)
    stdout, stderr, _timed_out, exit_code = communicate_process_group(
        proc,
        timeout=max(args.timeout * args.max_attempts + 120, args.timeout + 120),
        timeout_marker=f"{mode.upper()}_{fixture_id}_TIMEOUT",
    )
    elapsed = round(time.time() - started, 2)
    (run_root / f"{mode}_{fixture_id}.stdout.log").write_text(
        stdout, encoding="utf-8"
    )
    (run_root / f"{mode}_{fixture_id}.stderr.log").write_text(
        stderr, encoding="utf-8"
    )
    summary_path = case_dir / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    else:
        summary = {
            "mode": mode,
            "fixture": fixture_id,
            "proved": False,
            "process_exit_code": exit_code,
            "process_stdout_tail": stdout[-2000:],
            "process_stderr_tail": stderr[-2000:],
        }
    final_proof = summary.get("final_proof")
    features = summary.get("final_proof_features") or proof_features(final_proof)
    edit_summary = summary.get(
        "proof_edit_summary"
    ) or proof_edit_summary_from_attempts(summary)
    return {
        "fixture": fixture_id,
        "mode": mode,
        "category": fixture.get("category"),
        "difficulty": fixture.get("difficulty"),
        "proved": bool(summary.get("proved")),
        "final_attempt": summary.get("final_attempt"),
        "pi_calls": attempt_tool_calls(summary),
        "elapsed_seconds": elapsed,
        "process_exit_code": exit_code,
        "final_proof": final_proof,
        "proof_features": features,
        "feature_summary": proof_feature_summary(features),
        "proof_edit_summary": edit_summary,
        "summary_path": str(summary_path) if summary_path.exists() else None,
    }


def write_report(run_root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode: dict[str, dict[str, int]] = {}
    for row in rows:
        stats = by_mode.setdefault(row["mode"], {"total": 0, "proved": 0, "failed": 0})
        stats["total"] += 1
        if row["proved"]:
            stats["proved"] += 1
        else:
            stats["failed"] += 1
    feature_usage_by_mode = {
        mode: aggregate_feature_usage([row for row in rows if row["mode"] == mode])
        for mode in by_mode
    }
    proof_edit_usage_by_mode = {
        mode: aggregate_proof_edit_usage([row for row in rows if row["mode"] == mode])
        for mode in by_mode
    }
    aggregate = {
        "run_root": str(run_root),
        "by_mode": by_mode,
        "feature_usage_by_mode": feature_usage_by_mode,
        "proof_edit_usage_by_mode": proof_edit_usage_by_mode,
        "rows": rows,
    }
    (run_root / "direct_baseline_summary.json").write_text(
        json.dumps(aggregate, indent=2), encoding="utf-8"
    )
    lines = [
        "# Direct Pi baseline benchmark",
        "",
        f"Run root: `{run_root}`",
        "",
        "## Summary by mode",
        "",
    ]
    for mode, stats in by_mode.items():
        lines.append(
            f"- `{mode}`: {stats['proved']} / {stats['total']} proved, {stats['failed']} failed"
        )
    lines.extend(["", "## Feature usage by mode", ""])
    for mode, usage in feature_usage_by_mode.items():
        usage_text = (
            ", ".join(f"{name}={count}" for name, count in usage.items()) or "none"
        )
        lines.append(f"- `{mode}`: {usage_text}")
    lines.extend(["", "## Proof edit usage by mode", ""])
    for mode, usage in proof_edit_usage_by_mode.items():
        gained = usage.get("gained_feature_counts") or {}
        gained_text = (
            ", ".join(f"{name}={count}" for name, count in gained.items()) or "none"
        )
        lines.append(
            f"- `{mode}`: repairs={usage.get('repair_edits', 0)}, total_token_distance={usage.get('total_token_distance', 0)}, mean_tokens/edit={usage.get('mean_token_distance_per_edit', 0)}, gained={gained_text}"
        )
    lines.extend(
        [
            "",
            "## Results",
            "",
            "| Mode | Fixture | Category | Difficulty | Proved | Final attempt | Pi calls | Seconds | Features | Edit tokens | Final proof |",
            "|---|---|---|---:|---:|---:|---:|---:|---|---:|---|",
        ]
    )
    for row in rows:
        proof = proof_preview(row.get("final_proof"), limit=220)
        lines.append(
            "| {mode} | {fixture} | {category} | {difficulty} | {proved} | {final_attempt} | {pi_calls} | {seconds} | {features} | {edit_tokens} | `{proof}` |".format(
                mode=row["mode"],
                fixture=row["fixture"],
                category=row.get("category", ""),
                difficulty=row.get("difficulty", ""),
                proved="yes" if row.get("proved") else "no",
                final_attempt=row.get("final_attempt"),
                pi_calls=row.get("pi_calls"),
                seconds=row.get("elapsed_seconds"),
                features=row.get("feature_summary")
                or proof_feature_summary(row.get("final_proof")),
                edit_tokens=(row.get("proof_edit_summary") or {}).get(
                    "total_token_distance", 0
                ),
                proof=proof,
            )
        )
    lines.append("")
    (run_root / "direct_baseline_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(ROOT / "benchmark_manifest.json"))
    parser.add_argument("--fixtures", nargs="*")
    parser.add_argument("--max-fixtures", type=int)
    parser.add_argument(
        "--modes",
        nargs="+",
        default=["one-shot", "repair-loop"],
        choices=["one-shot", "repair-loop"],
    )
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--pi-provider")
    parser.add_argument("--pi-model")
    parser.add_argument("--thinking")
    parser.add_argument("--run-root")
    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest))
    fixtures = selected_fixtures(manifest, args.fixtures, args.max_fixtures)
    run_root = resolve_run_root(args.run_root, "direct_pi_baselines")
    run_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for mode in args.modes:
        for fixture in fixtures:
            row = run_case(fixture=fixture, mode=mode, run_root=run_root, args=args)
            rows.append(row)
            aggregate = write_report(run_root, rows)
            print(
                json.dumps(
                    {"mode": mode, "fixture": fixture["id"], "proved": row["proved"]}
                ),
                flush=True,
            )
    aggregate = write_report(run_root, rows)
    print(json.dumps(aggregate, indent=2))
    failures = sum(stats["failed"] for stats in aggregate["by_mode"].values())
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
