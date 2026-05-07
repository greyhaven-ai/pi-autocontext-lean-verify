#!/usr/bin/env python3
"""Verify bundled expected Lean proof bodies against fixed templates."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
HARNESS = PACKAGE / "harness"
MANIFEST = HARNESS / "benchmark_manifest.json"
DEFAULT_LEAN = Path("/tmp/autocontext-elan-home/bin/lean")


def lean_binary() -> str:
    configured = os.environ.get("LEAN")
    if configured:
        return configured
    if DEFAULT_LEAN.exists():
        return str(DEFAULT_LEAN)
    found = shutil.which("lean")
    if found:
        return found
    raise RuntimeError(
        "Lean binary not found. Set LEAN, install Lean on PATH, or use /tmp/autocontext-elan-home/bin/lean."
    )


def elan_home_for_lean(lean: str) -> str | None:
    if os.environ.get("ELAN_HOME"):
        return os.environ["ELAN_HOME"]
    path = Path(lean)
    if path.name == "lean" and path.parent.name == "bin":
        return str(path.parent.parent)
    return None


def fixture_ids() -> list[str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [fixture["id"] for fixture in manifest["fixtures"]]


def verify_fixture(fixture: str, lean: str, env: dict[str, str], tmpdir: Path) -> tuple[bool, str]:
    fixture_dir = HARNESS / "fixtures" / fixture
    template = (fixture_dir / "Theorem.template.lean").read_text(encoding="utf-8")
    proof = (fixture_dir / "expected_proof.lean").read_text(encoding="utf-8")
    candidate = tmpdir / f"{fixture}.lean"
    candidate.write_text(template.replace("{{PROOF}}", proof), encoding="utf-8")
    result = subprocess.run(
        [lean, str(candidate)],
        cwd=HARNESS,
        text=True,
        capture_output=True,
        env=env,
        timeout=30,
        check=False,
    )
    if result.returncode == 0:
        return True, ""
    return False, (result.stdout + "\n" + result.stderr).strip()


def main() -> int:
    lean = lean_binary()
    env = os.environ.copy()
    elan_home = elan_home_for_lean(lean)
    if elan_home:
        env["ELAN_HOME"] = elan_home
    failures: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="lean-expected-proofs-") as tmp:
        tmpdir = Path(tmp)
        for fixture in fixture_ids():
            ok, output = verify_fixture(fixture, lean, env, tmpdir)
            if not ok:
                failures[fixture] = output
    total = len(fixture_ids())
    print(f"Lean binary: {lean}")
    print(f"manifest_fixtures={total}")
    print(f"expected_proofs_verified={total - len(failures)} failed={len(failures)}")
    if failures:
        for fixture, output in failures.items():
            print(f"\n## {fixture}\n{output}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
