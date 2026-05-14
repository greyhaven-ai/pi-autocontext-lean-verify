#!/usr/bin/env python3
"""Run a reproducible seeded-autocontext vs direct-Pi Lean proof benchmark.

The benchmark preserves the package guardrails:
- candidate supplies only the proof body for {{PROOF}}
- Lean verification is the only success oracle
- seeded autocontext runs use no pregeneration and no synthetic hint candidates
"""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from process_utils import communicate_process_group, popen_process_group

ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = ROOT.parent
FIXTURE_GROUPS = PACKAGE_ROOT / "fixture_groups.json"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def default_run_root(kind: str, fixture_group: str) -> Path:
    return Path(tempfile.gettempdir()) / "pi-autocontext-lean-verify" / f"{utc_stamp()}_{kind}_{fixture_group}"


def load_fixture_group(name: str) -> list[str]:
    data = json.loads(FIXTURE_GROUPS.read_text(encoding="utf-8"))
    groups = data.get("groups", {})
    if name not in groups:
        raise SystemExit(f"Unknown fixture group {name!r}; known groups: {', '.join(sorted(groups))}")
    return list(groups[name])


def default_seed_playbook(group: str) -> Path:
    if group == "challenge_v25_step_prefix_exact_labels":
        seed = ROOT / "playbooks" / "challenge_v25_step_prefix_exact_labels_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v24_plan_prefix_generic_labels":
        seed = ROOT / "playbooks" / "challenge_v24_plan_prefix_generic_labels_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v23_exact_labels_without_plan_prefix":
        seed = ROOT / "playbooks" / "challenge_v23_exact_labels_without_plan_prefix_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v22_code_like_anchor_skeleton":
        seed = ROOT / "playbooks" / "challenge_v22_code_like_anchor_skeleton_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v21_neutral_anchor_skeleton":
        seed = ROOT / "playbooks" / "challenge_v21_neutral_anchor_skeleton_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v20_description_only_skeleton":
        seed = ROOT / "playbooks" / "challenge_v20_description_only_skeleton_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v19_bare_skeleton_names":
        seed = ROOT / "playbooks" / "challenge_v19_bare_skeleton_names_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v18_prompt_only_skeleton_hints":
        seed = ROOT / "playbooks" / "challenge_v18_prompt_only_skeleton_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v7_frontier":
        seed = ROOT / "playbooks" / "challenge_v6_frontier_v1.md"
        if seed.exists():
            return seed
        seed = ROOT / "playbooks" / "challenge_v5_attribution_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v6_frontier":
        seed = ROOT / "playbooks" / "challenge_v5_attribution_v1.md"
        if seed.exists():
            return seed
        seed = ROOT / "playbooks" / "challenge_v4_count_v1.md"
        if seed.exists():
            return seed
    if group in {"challenge_v5_attribution", "challenge_v5_tree_tally"}:
        seed = ROOT / "playbooks" / "challenge_v4_count_v1.md"
        if seed.exists():
            return seed
    if group == "challenge_v4_count":
        seed = ROOT / "playbooks" / "challenge_v3_generalization_v1.md"
        if seed.exists():
            return seed
    if group in {"challenge_v3_generalization", "challenge_transfer", "challenge_extended_transfer"}:
        challenge_seed = ROOT / "playbooks" / "challenge_v2_no_helper_v1.md"
        if challenge_seed.exists():
            return challenge_seed
    return ROOT / "playbooks" / "expanded_mixed_cluster_v1.md"


def run_command(
    *,
    name: str,
    cmd: list[str],
    cwd: Path,
    log_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    started = time.time()
    proc = popen_process_group(cmd, cwd=cwd)
    stdout, stderr, _timed_out, exit_code = communicate_process_group(
        proc,
        timeout=timeout_seconds,
        timeout_marker=f"{name.upper()}_TIMEOUT after {timeout_seconds}s",
    )
    elapsed = round(time.time() - started, 2)
    (log_dir / f"{name}.stdout.log").write_text(stdout, encoding="utf-8")
    (log_dir / f"{name}.stderr.log").write_text(stderr, encoding="utf-8")
    (log_dir / f"{name}.command.json").write_text(
        json.dumps(cmd, indent=2), encoding="utf-8"
    )
    return {
        "name": name,
        "exit_code": exit_code,
        "elapsed_seconds": elapsed,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
    }


def direct_elapsed(summary: dict[str, Any]) -> float:
    return round(sum(float(row.get("elapsed_seconds") or 0) for row in summary.get("rows", [])), 2)


def direct_pi_calls(summary: dict[str, Any]) -> int:
    return sum(int(row.get("pi_calls") or 0) for row in summary.get("rows", []))


def transfer_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    metrics = summary.get("trigger_cost_metrics") or {}
    return {
        "proved": int(summary.get("proved") or 0),
        "total": int(summary.get("total") or 0),
        "failed": int(summary.get("failed") or 0),
        "pi_calls": int(metrics.get("pi_calls") or 0),
        "pi_elapsed_seconds": float(metrics.get("pi_elapsed_seconds") or 0),
        "lean_verifier_attempts": int(metrics.get("total_lean_verifier_attempts") or 0),
        "pregenerate_calls": int(metrics.get("pregenerate_calls") or 0),
        "hint_candidates_generated": int(metrics.get("strategy_hint_candidates_generated") or 0)
        + int(metrics.get("pre_repair_strategy_hint_candidates_generated") or 0),
    }


def direct_metrics(summary: dict[str, Any], mode: str = "repair-loop") -> dict[str, Any]:
    stats = (summary.get("by_mode") or {}).get(mode, {})
    return {
        "proved": int(stats.get("proved") or 0),
        "total": int(stats.get("total") or 0),
        "failed": int(stats.get("failed") or 0),
        "pi_calls": direct_pi_calls(summary),
        "pi_elapsed_seconds": direct_elapsed(summary),
        "lean_verifier_attempts": None,
        "pregenerate_calls": None,
        "hint_candidates_generated": None,
    }


def failure_class(row: dict[str, Any]) -> str:
    if row.get("proved"):
        return "proved"
    final = str(row.get("final_proof") or "").strip()
    elapsed = float(row.get("elapsed_seconds") or 0)
    if final == "rfl" and elapsed >= 0:
        return "timeout/no extracted repair" if elapsed >= 100 else "no nontrivial repair extracted"
    return "Lean verification failed"


def write_report(
    *,
    run_root: Path,
    fixture_group: str,
    fixtures: list[str],
    seed_playbook: Path,
    transfer_summary: dict[str, Any] | None,
    direct_summary: dict[str, Any] | None,
    command_results: list[dict[str, Any]],
) -> dict[str, Any]:
    transfer = transfer_metrics(transfer_summary or {}) if transfer_summary else None
    direct = direct_metrics(direct_summary or {}) if direct_summary else None
    aggregate = {
        "type": "proof-transfer-benchmark",
        "run_root": str(run_root),
        "fixture_group": fixture_group,
        "fixtures": fixtures,
        "seed_playbook": str(seed_playbook),
        "methods": {
            "seeded_autocontext": transfer,
            "direct_pi_repair_loop": direct,
        },
        "commands": command_results,
        "autocontext_rows": (transfer_summary or {}).get("rows", []),
        "direct_rows": (direct_summary or {}).get("rows", []),
    }
    (run_root / "proof_transfer_benchmark_summary.json").write_text(
        json.dumps(aggregate, indent=2), encoding="utf-8"
    )

    lines = [
        "# Proof-transfer benchmark",
        "",
        f"Run root: `{run_root}`",
        f"Fixture group: `{fixture_group}`",
        f"Fixtures: {', '.join(f'`{fixture}`' for fixture in fixtures)}",
        f"Seed playbook: `{seed_playbook}`",
        "",
        "## Guardrails",
        "",
        "- Seeded autocontext uses `--no-pregenerate` and `--structured-alternate-retry` only.",
        "- Synthetic hint candidates are disabled.",
        "- Lean verification is the only success oracle.",
        "- Direct baseline uses `repair-loop` with the same fixture set.",
        "",
        "## Summary",
        "",
        "| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts | Pregenerate/hint calls |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    if transfer:
        lines.append(
            f"| seeded_autocontext | {transfer['proved']}/{transfer['total']} | {transfer['pi_calls']} | {transfer['pi_elapsed_seconds']:.2f}s | {transfer['lean_verifier_attempts']} | {transfer['pregenerate_calls']}/{transfer['hint_candidates_generated']} |"
        )
    if direct:
        lines.append(
            f"| direct_pi_repair_loop | {direct['proved']}/{direct['total']} | {direct['pi_calls']} | {direct['pi_elapsed_seconds']:.2f}s | n/a | n/a |"
        )

    lines.extend([
        "",
        "## Fixture-level results",
        "",
        "| Fixture | Seeded autocontext | Direct repair-loop | Direct failure class |",
        "| --- | ---: | ---: | --- |",
    ])
    transfer_rows = {row.get("fixture"): row for row in (transfer_summary or {}).get("rows", [])}
    direct_rows = {row.get("fixture"): row for row in (direct_summary or {}).get("rows", [])}
    for fixture in fixtures:
        trow = transfer_rows.get(fixture, {})
        drow = direct_rows.get(fixture, {})
        tcell = "missing"
        dcell = "missing"
        if trow:
            tcell = f"{'proved' if trow.get('proved') else 'failed'} ({float(trow.get('elapsed_seconds') or 0):.2f}s)"
        if drow:
            dcell = f"{'proved' if drow.get('proved') else 'failed'} ({float(drow.get('elapsed_seconds') or 0):.2f}s)"
        lines.append(f"| `{fixture}` | {tcell} | {dcell} | {failure_class(drow) if drow else 'missing'} |")

    lines.extend(["", "## Command exits", ""])
    for result in command_results:
        lines.append(
            f"- `{result['name']}`: exit={result['exit_code']}, elapsed={result['elapsed_seconds']}s"
        )
    lines.append("")
    (run_root / "proof_transfer_benchmark_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-group", default="challenge_v3_generalization")
    parser.add_argument("--fixtures", nargs="*")
    parser.add_argument("--seed-playbook")
    parser.add_argument("--run-root")
    parser.add_argument("--provider", default="pi")
    parser.add_argument("--package-version", default="0.5.1")
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--direct-modes", nargs="+", default=["repair-loop"])
    args = parser.parse_args()

    fixtures = args.fixtures or load_fixture_group(args.fixture_group)
    seed_playbook = Path(args.seed_playbook) if args.seed_playbook else default_seed_playbook(args.fixture_group)
    if not seed_playbook.is_absolute():
        seed_playbook = (ROOT / seed_playbook).resolve()
    run_root = Path(args.run_root) if args.run_root else default_run_root("proof_transfer_benchmark", args.fixture_group)
    if not run_root.is_absolute():
        run_root = ROOT / run_root
    run_root.mkdir(parents=True, exist_ok=True)

    seeded_root = run_root / "seeded_autocontext"
    direct_root = run_root / "direct_pi_repair_loop"
    command_results: list[dict[str, Any]] = []

    seeded_cmd = [
        "python3",
        "run_playbook_transfer.py",
        "--fixtures",
        *fixtures,
        "--seed-playbook",
        str(seed_playbook),
        "--no-pregenerate",
        "--structured-alternate-retry",
        "--max-attempts",
        str(args.max_attempts),
        "--rounds",
        str(args.rounds),
        "--timeout",
        str(args.timeout),
        "--provider",
        args.provider,
        "--package-version",
        args.package_version,
        "--run-root",
        str(seeded_root),
    ]
    command_results.append(
        run_command(
            name="seeded_autocontext",
            cmd=seeded_cmd,
            cwd=ROOT,
            log_dir=run_root,
            timeout_seconds=max(args.timeout * len(fixtures) * args.max_attempts + 240, 300),
        )
    )

    direct_cmd = [
        "python3",
        "run_direct_baseline_benchmark.py",
        "--fixtures",
        *fixtures,
        "--modes",
        *args.direct_modes,
        "--max-attempts",
        str(args.max_attempts),
        "--timeout",
        str(args.timeout),
        "--pi-provider",
        args.provider,
        "--run-root",
        str(direct_root),
    ]
    command_results.append(
        run_command(
            name="direct_pi_repair_loop",
            cmd=direct_cmd,
            cwd=ROOT,
            log_dir=run_root,
            timeout_seconds=max(args.timeout * len(fixtures) * args.max_attempts + 240, 300),
        )
    )

    transfer_path = seeded_root / "transfer_summary.json"
    direct_path = direct_root / "direct_baseline_summary.json"
    transfer_summary = json.loads(transfer_path.read_text(encoding="utf-8")) if transfer_path.exists() else None
    direct_summary = json.loads(direct_path.read_text(encoding="utf-8")) if direct_path.exists() else None
    aggregate = write_report(
        run_root=run_root,
        fixture_group=args.fixture_group,
        fixtures=fixtures,
        seed_playbook=seed_playbook,
        transfer_summary=transfer_summary,
        direct_summary=direct_summary,
        command_results=command_results,
    )
    print(json.dumps(aggregate, indent=2))

    seeded_ok = bool(transfer_summary and transfer_summary.get("proved") == transfer_summary.get("total"))
    return 0 if seeded_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
