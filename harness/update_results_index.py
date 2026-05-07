#!/usr/bin/env python3
"""Build a persistent index of saved Lean proof experiment results.

All experiment scripts already write per-run artifacts under `results/`. This script
collects the high-level summaries into:

- results/index.json
- results/EXPERIMENTS.md

Run it after any experiment to keep a durable ledger.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiment_common import ROOT, aggregate_feature_usage, aggregate_proof_edit_usage

RESULTS = ROOT / "results"
SUMMARY_FILES = [
    "repeated_comparison_summary.json",
    "direct_baseline_summary.json",
    "batch_summary.json",
    "combined_summary.json",
    "comparison_summary.json",
    "transfer_summary.json",
    "variance_summary.json",
]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def classify(path: Path, data: dict[str, Any]) -> str:
    name = path.name
    if name == "repeated_comparison_summary.json":
        return "repeated-comparison"
    if name == "direct_baseline_summary.json":
        return "direct-baseline"
    if name == "batch_summary.json":
        return "autocontext-batch"
    if name == "combined_summary.json":
        return "combined"
    if name == "comparison_summary.json":
        return "comparison"
    if name == "transfer_summary.json":
        return "playbook-transfer"
    if name == "variance_summary.json":
        return "variance-summary"
    return str(data.get("type") or "unknown")


def _aggregate_edits_by_key(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get(key):
            grouped[str(row[key])].append(row)
    return {
        name: aggregate_proof_edit_usage(group_rows)
        for name, group_rows in grouped.items()
    }


def summarize(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    run_dir = path.parent
    kind = classify(path, data)
    rel_run_dir = run_dir.relative_to(ROOT)
    item: dict[str, Any] = {
        "kind": kind,
        "run_dir": str(rel_run_dir),
        "summary_path": str(path.relative_to(ROOT)),
        "modified_utc": datetime.fromtimestamp(
            path.stat().st_mtime, timezone.utc
        ).isoformat(),
    }
    if kind == "repeated-comparison":
        item["by_method"] = data.get("by_method", {})
        item["feature_usage"] = aggregate_feature_usage(data.get("rows", []))
        item["feature_usage_by_method"] = data.get("feature_usage_by_method", {})
        item["proof_edit_usage"] = data.get(
            "proof_edit_usage"
        ) or aggregate_proof_edit_usage(data.get("rows", []))
        item["proof_edit_usage_by_method"] = data.get(
            "proof_edit_usage_by_method"
        ) or _aggregate_edits_by_key(data.get("rows", []), "method")
        item["fixtures"] = sorted(
            {row.get("fixture") for row in data.get("rows", []) if row.get("fixture")}
        )
        item["trials"] = sorted(
            {row.get("trial") for row in data.get("rows", []) if row.get("trial")}
        )
    elif kind == "direct-baseline":
        item["by_mode"] = data.get("by_mode", {})
        item["feature_usage"] = aggregate_feature_usage(data.get("rows", []))
        item["feature_usage_by_mode"] = data.get("feature_usage_by_mode", {})
        item["proof_edit_usage"] = data.get(
            "proof_edit_usage"
        ) or aggregate_proof_edit_usage(data.get("rows", []))
        item["proof_edit_usage_by_mode"] = data.get(
            "proof_edit_usage_by_mode"
        ) or _aggregate_edits_by_key(data.get("rows", []), "mode")
        item["fixtures"] = sorted(
            {row.get("fixture") for row in data.get("rows", []) if row.get("fixture")}
        )
    elif kind == "autocontext-batch":
        item["total"] = data.get("total")
        item["proved"] = data.get("proved")
        item["failed"] = data.get("failed")
        item["feature_usage"] = data.get("feature_usage") or aggregate_feature_usage(
            data.get("rows", [])
        )
        item["proof_edit_usage"] = data.get(
            "proof_edit_usage"
        ) or aggregate_proof_edit_usage(data.get("rows", []))
        item["fixtures"] = [row.get("fixture") for row in data.get("rows", [])]
    elif kind == "combined":
        item["total"] = data.get("total")
        item["proved"] = data.get("proved")
        item["failed"] = data.get("failed")
        item["feature_usage"] = data.get("feature_usage") or aggregate_feature_usage(
            data.get("rows", [])
        )
        item["proof_edit_usage"] = data.get(
            "proof_edit_usage"
        ) or aggregate_proof_edit_usage(data.get("rows", []))
        item["fixtures"] = [row.get("fixture") for row in data.get("rows", [])]
        item["source_runs"] = data.get("source_runs", [])
    elif kind == "comparison":
        item["total_common_fixtures"] = data.get("total_common_fixtures")
        item["autocontext_proved"] = data.get("autocontext_proved")
        item["direct_one_shot_proved"] = data.get("direct_one_shot_proved")
        item["direct_repair_proved"] = data.get("direct_repair_proved")
        item["feature_usage"] = data.get("feature_usage") or aggregate_feature_usage(
            [
                {
                    "proved": row.get("autocontext_proved"),
                    "final_proof": row.get("autocontext_final_proof"),
                    "proof_features": row.get("autocontext_proof_features"),
                }
                for row in data.get("rows", [])
            ]
        )
        item["proof_edit_usage"] = data.get(
            "proof_edit_usage"
        ) or aggregate_proof_edit_usage(
            [
                {
                    "proved": row.get("autocontext_proved"),
                    "proof_edit_summary": row.get("autocontext_proof_edit_summary"),
                }
                for row in data.get("rows", [])
            ]
        )
        item["autocontext_only_successes"] = data.get("autocontext_only_successes", [])
    elif kind == "playbook-transfer":
        item["total"] = data.get("total")
        item["proved"] = data.get("proved")
        item["failed"] = data.get("failed")
        item["final_playbook_entries"] = data.get("final_playbook_entries")
        item["feature_usage"] = data.get("feature_usage") or aggregate_feature_usage(
            data.get("rows", [])
        )
        item["proof_edit_usage"] = data.get(
            "proof_edit_usage"
        ) or aggregate_proof_edit_usage(data.get("rows", []))
        item["fixtures"] = data.get("fixtures", [])
    elif kind == "variance-summary":
        aggregate = (
            data.get("aggregate")
            or data.get("pre_repair_aggregate")
            or data.get("post_repair_hint_baseline_aggregate")
            or data.get("no_hint_structured_retry_baseline_aggregate")
            or {}
        )
        item["fixture_trials"] = aggregate.get("fixture_trials")
        item["proved_fixture_trials"] = aggregate.get("proved_fixture_trials")
        item["failed_fixture_trials"] = aggregate.get("failed_fixture_trials")
        item["fixture_trial_success_rate"] = aggregate.get("fixture_trial_success_rate")
        item["runs_with_all_fixtures_proved"] = aggregate.get(
            "runs_with_all_fixtures_proved"
        )
        item["trials"] = aggregate.get("trials")
        item["proved_per_run"] = aggregate.get("proved_per_run", {})
        item["proof_edit_usage"] = {
            "repair_edits": aggregate.get("total_repair_edits", 0),
            "total_token_distance": aggregate.get("total_token_distance", 0),
            "mean_token_distance_per_edit": aggregate.get(
                "mean_token_distance_per_edit_overall", 0
            ),
        }
        item["fixtures"] = data.get("fixtures", [])
        item["run_roots"] = data.get("run_roots", [])
    return item


def scan_results() -> list[dict[str, Any]]:
    if not RESULTS.exists():
        return []
    items: list[dict[str, Any]] = []
    for summary_name in SUMMARY_FILES:
        for path in RESULTS.rglob(summary_name):
            data = load_json(path)
            if data is None:
                continue
            items.append(summarize(path, data))
    return sorted(items, key=lambda item: item["run_dir"])


def feature_usage_text(usage: dict[str, Any]) -> str:
    if not usage:
        return ""
    return ", ".join(f"{name}={count}" for name, count in usage.items())


def proof_edit_usage_text(usage: dict[str, Any]) -> str:
    if not usage:
        return ""
    repairs = usage.get("repair_edits", 0)
    tokens = usage.get("total_token_distance", 0)
    mean = usage.get("mean_token_distance_per_edit", 0)
    return f"repairs={repairs}, tok={tokens}, mean/edit={mean}"


def method_stats_text(stats: dict[str, Any]) -> str:
    if not stats:
        return ""
    parts: list[str] = []
    for name, values in sorted(stats.items()):
        total = values.get("total")
        proved = values.get("proved")
        failed = values.get("failed")
        rate = values.get("success_rate")
        if total is not None and proved is not None:
            suffix = f", rate={rate}" if rate is not None else ""
            parts.append(f"{name}: {proved}/{total} proved, failed={failed}{suffix}")
    return "; ".join(parts)


def write_markdown(index: dict[str, Any]) -> None:
    lines = [
        "# Formal-proof Lean pilot experiment index",
        "",
        f"Generated: `{index['generated_utc']}`",
        "",
        "This ledger is generated from saved JSON summaries under `results/`. Each run directory contains the full prompts, candidate proofs, Lean verifier artifacts, stdout/stderr logs, and summary JSON files.",
        "",
        "## Runs",
        "",
        "| Kind | Run directory | Summary | Outcome | Features | Proof edits | Fixtures |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in index["runs"]:
        outcome = ""
        if item["kind"] == "repeated-comparison":
            outcome = method_stats_text(item.get("by_method", {}))
        elif item["kind"] == "direct-baseline":
            outcome = method_stats_text(item.get("by_mode", {}))
        elif item["kind"] in {"autocontext-batch", "combined"}:
            outcome = f"{item.get('proved')}/{item.get('total')} proved, failed={item.get('failed')}"
        elif item["kind"] == "comparison":
            outcome = (
                f"auto={item.get('autocontext_proved')}, "
                f"one-shot={item.get('direct_one_shot_proved')}, "
                f"repair={item.get('direct_repair_proved')}"
            )
        elif item["kind"] == "playbook-transfer":
            outcome = (
                f"{item.get('proved')}/{item.get('total')} proved, "
                f"failed={item.get('failed')}, "
                f"entries={item.get('final_playbook_entries')}"
            )
        elif item["kind"] == "variance-summary":
            proved_per_run = item.get("proved_per_run", {})
            outcome = (
                f"{item.get('proved_fixture_trials')}/{item.get('fixture_trials')} fixture-trials, "
                f"all-runs={item.get('runs_with_all_fixtures_proved')}/{item.get('trials')}, "
                f"proved/run mean={proved_per_run.get('mean')}"
            )
        fixtures = item.get("fixtures") or item.get("autocontext_only_successes") or []
        fixture_text = ", ".join(str(fixture) for fixture in fixtures[:8])
        if len(fixtures) > 8:
            fixture_text += f", … (+{len(fixtures) - 8})"
        features = feature_usage_text(item.get("feature_usage", {}))
        edits = proof_edit_usage_text(item.get("proof_edit_usage", {}))
        lines.append(
            f"| {item['kind']} | `{item['run_dir']}` | `{item['summary_path']}` | {outcome} | {features} | {edits} | {fixture_text} |"
        )
    lines.append("")
    (RESULTS / "EXPERIMENTS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    index = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "runs": scan_results(),
    }
    (RESULTS / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    write_markdown(index)
    print(
        json.dumps(
            {
                "runs_indexed": len(index["runs"]),
                "index": str(RESULTS / "index.json"),
                "markdown": str(RESULTS / "EXPERIMENTS.md"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
