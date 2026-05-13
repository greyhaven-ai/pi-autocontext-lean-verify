#!/usr/bin/env python3
"""Run seeded, unseeded-isolated, and direct-Pi Lean proof attribution benchmark."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    if group in {
        "challenge_v8_diagnostics",
        "challenge_v9_composition_gradient",
        "challenge_v10_stats_reification",
        "challenge_v11_metric_composition",
        "challenge_v12_simultaneous_metrics",
        "challenge_v13_decomposition_order",
        "challenge_v14_metric_order_permutations",
        "challenge_v15_proof_shape_hints",
        "challenge_v16_compact_reassembly_hints",
        "challenge_v17_proof_plan_hints",
    }:
        seed = ROOT / "playbooks" / "challenge_v6_frontier_v1.md"
        if seed.exists():
            return seed
        seed = ROOT / "playbooks" / "challenge_v5_attribution_v1.md"
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
        seed = ROOT / "playbooks" / "challenge_v2_no_helper_v1.md"
        if seed.exists():
            return seed
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
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
        exit_code = proc.returncode
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
        stderr += f"\n{name.upper()}_TIMEOUT after {timeout_seconds}s\n"
        exit_code = 124
    elapsed = round(time.time() - started, 2)
    (log_dir / f"{name}.stdout.log").write_text(stdout, encoding="utf-8")
    (log_dir / f"{name}.stderr.log").write_text(stderr, encoding="utf-8")
    (log_dir / f"{name}.command.json").write_text(json.dumps(cmd, indent=2), encoding="utf-8")
    return {
        "name": name,
        "exit_code": exit_code,
        "elapsed_seconds": elapsed,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
    }


def transfer_metrics(summary: dict[str, Any] | None) -> dict[str, Any] | None:
    if not summary:
        return None
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


def direct_metrics(summary: dict[str, Any] | None) -> dict[str, Any] | None:
    if not summary:
        return None
    stats = (summary.get("by_mode") or {}).get("repair-loop", {})
    rows = summary.get("rows", [])
    return {
        "proved": int(stats.get("proved") or 0),
        "total": int(stats.get("total") or 0),
        "failed": int(stats.get("failed") or 0),
        "pi_calls": sum(int(row.get("pi_calls") or 0) for row in rows),
        "pi_elapsed_seconds": round(sum(float(row.get("elapsed_seconds") or 0) for row in rows), 2),
        "lean_verifier_attempts": None,
        "pregenerate_calls": None,
        "hint_candidates_generated": None,
    }


def aggregate_unseeded(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    metrics = [transfer_metrics(summary) for summary in summaries.values()]
    metrics = [metric for metric in metrics if metric]
    return {
        "proved": sum(metric["proved"] for metric in metrics),
        "total": sum(metric["total"] for metric in metrics),
        "failed": sum(metric["failed"] for metric in metrics),
        "pi_calls": sum(metric["pi_calls"] for metric in metrics),
        "pi_elapsed_seconds": round(sum(metric["pi_elapsed_seconds"] for metric in metrics), 2),
        "lean_verifier_attempts": sum(metric["lean_verifier_attempts"] for metric in metrics),
        "pregenerate_calls": sum(metric["pregenerate_calls"] for metric in metrics),
        "hint_candidates_generated": sum(metric["hint_candidates_generated"] for metric in metrics),
    }


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def method_row(stats: dict[str, Any] | None) -> str:
    if not stats:
        return "missing"
    return f"{stats['proved']} / {stats['total']}"


def write_report(
    *,
    run_root: Path,
    fixture_group: str,
    fixtures: list[str],
    seed_playbook: Path,
    seeded_summary: dict[str, Any] | None,
    unseeded_summaries: dict[str, dict[str, Any]],
    direct_summary: dict[str, Any] | None,
    command_results: list[dict[str, Any]],
) -> dict[str, Any]:
    seeded = transfer_metrics(seeded_summary)
    unseeded = aggregate_unseeded(unseeded_summaries)
    direct = direct_metrics(direct_summary)
    seeded_rows = {row.get("fixture"): row for row in (seeded_summary or {}).get("rows", [])}
    direct_rows = {row.get("fixture"): row for row in (direct_summary or {}).get("rows", [])}
    unseeded_rows = {
        fixture: (summary.get("rows") or [{}])[0]
        for fixture, summary in unseeded_summaries.items()
    }
    aggregate = {
        "type": "proof-transfer-attribution-benchmark",
        "run_root": str(run_root),
        "fixture_group": fixture_group,
        "fixtures": fixtures,
        "seed_playbook": str(seed_playbook),
        "methods": {
            "seeded_autocontext": seeded,
            "unseeded_isolated_autocontext": unseeded,
            "direct_pi_repair_loop": direct,
        },
        "commands": command_results,
        "seeded_rows": list(seeded_rows.values()),
        "unseeded_rows": unseeded_rows,
        "direct_rows": list(direct_rows.values()),
    }
    (run_root / "attribution_benchmark_summary.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")

    lines = [
        "# Proof-transfer attribution benchmark",
        "",
        f"Run root: `{run_root}`",
        f"Fixture group: `{fixture_group}`",
        f"Fixtures: {', '.join(f'`{fixture}`' for fixture in fixtures)}",
        f"Seed playbook: `{seed_playbook}`",
        "",
        "## Guardrails",
        "",
        "- Seeded and unseeded autocontext use `--no-pregenerate` and `--structured-alternate-retry` only.",
        "- Synthetic hint candidates are disabled.",
        "- Lean verification is the only success oracle.",
        "- Direct baseline uses `repair-loop` with the same fixture set.",
        "",
        "## Summary",
        "",
        "| Method | Proved | Pi calls | Pi elapsed | Lean verifier attempts | Pregenerate/hint calls |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, stats in [
        ("seeded_autocontext", seeded),
        ("unseeded_isolated_autocontext", unseeded),
        ("direct_pi_repair_loop", direct),
    ]:
        if not stats:
            continue
        lean = stats["lean_verifier_attempts"] if stats["lean_verifier_attempts"] is not None else "n/a"
        pregenerate = stats["pregenerate_calls"] if stats["pregenerate_calls"] is not None else "n/a"
        hints = stats["hint_candidates_generated"] if stats["hint_candidates_generated"] is not None else "n/a"
        lines.append(
            f"| {name} | {stats['proved']} / {stats['total']} | {stats['pi_calls']} | {stats['pi_elapsed_seconds']:.2f}s | {lean} | {pregenerate}/{hints} |"
        )
    lines.extend([
        "",
        "## Fixture-level results",
        "",
        "| Fixture | Seeded | Unseeded isolated | Direct repair-loop |",
        "| --- | ---: | ---: | ---: |",
    ])
    for fixture in fixtures:
        srow = seeded_rows.get(fixture, {})
        urow = unseeded_rows.get(fixture, {})
        drow = direct_rows.get(fixture, {})
        lines.append(
            f"| `{fixture}` | {'proved' if srow.get('proved') else 'failed'} | {'proved' if urow.get('proved') else 'failed'} | {'proved' if drow.get('proved') else 'failed'} |"
        )
    lines.extend(["", "## Command exits", ""])
    for result in command_results:
        lines.append(f"- `{result['name']}`: exit={result['exit_code']}, elapsed={result['elapsed_seconds']}s")
    lines.append("")
    (run_root / "attribution_benchmark_report.md").write_text("\n".join(lines), encoding="utf-8")
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-group", default="challenge_v5_attribution")
    parser.add_argument("--fixtures", nargs="*")
    parser.add_argument("--seed-playbook")
    parser.add_argument("--run-root")
    parser.add_argument("--provider", default="pi")
    parser.add_argument("--package-version", default="0.4.8")
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    fixtures = args.fixtures or load_fixture_group(args.fixture_group)
    seed_playbook = Path(args.seed_playbook) if args.seed_playbook else default_seed_playbook(args.fixture_group)
    if not seed_playbook.is_absolute():
        seed_playbook = (ROOT / seed_playbook).resolve()
    run_root = Path(args.run_root) if args.run_root else default_run_root("attribution_benchmark", args.fixture_group)
    if not run_root.is_absolute():
        run_root = ROOT / run_root
    run_root.mkdir(parents=True, exist_ok=True)

    single_fixture_timeout = max(args.timeout * args.max_attempts * 8 + 600, 1800)
    command_timeout = max(single_fixture_timeout * max(len(fixtures), 1), 3600)
    command_results: list[dict[str, Any]] = []

    seeded_root = run_root / "seeded_autocontext"
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
    command_results.append(run_command(name="seeded_autocontext", cmd=seeded_cmd, cwd=ROOT, log_dir=run_root, timeout_seconds=command_timeout))

    unseeded_summaries: dict[str, dict[str, Any]] = {}
    for fixture in fixtures:
        unseeded_root = run_root / "unseeded_isolated" / fixture
        unseeded_cmd = [
            "python3",
            "run_playbook_transfer.py",
            "--fixtures",
            fixture,
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
            str(unseeded_root),
        ]
        command_results.append(run_command(name=f"unseeded_{fixture}", cmd=unseeded_cmd, cwd=ROOT, log_dir=run_root, timeout_seconds=single_fixture_timeout))
        summary = read_json_if_exists(unseeded_root / "transfer_summary.json")
        if summary:
            unseeded_summaries[fixture] = summary

    direct_root = run_root / "direct_pi_repair_loop"
    direct_cmd = [
        "python3",
        "run_direct_baseline_benchmark.py",
        "--fixtures",
        *fixtures,
        "--modes",
        "repair-loop",
        "--max-attempts",
        str(args.max_attempts),
        "--timeout",
        str(args.timeout),
        "--pi-provider",
        args.provider,
        "--run-root",
        str(direct_root),
    ]
    command_results.append(run_command(name="direct_pi_repair_loop", cmd=direct_cmd, cwd=ROOT, log_dir=run_root, timeout_seconds=command_timeout))

    seeded_summary = read_json_if_exists(seeded_root / "transfer_summary.json")
    direct_summary = read_json_if_exists(direct_root / "direct_baseline_summary.json")
    aggregate = write_report(
        run_root=run_root,
        fixture_group=args.fixture_group,
        fixtures=fixtures,
        seed_playbook=seed_playbook,
        seeded_summary=seeded_summary,
        unseeded_summaries=unseeded_summaries,
        direct_summary=direct_summary,
        command_results=command_results,
    )
    print(json.dumps(aggregate, indent=2))
    seeded_ok = bool(seeded_summary and seeded_summary.get("proved") == seeded_summary.get("total"))
    return 0 if seeded_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
