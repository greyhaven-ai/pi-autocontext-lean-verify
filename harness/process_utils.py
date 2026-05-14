"""Subprocess helpers that clean up complete child process groups.

The Lean/Pi/autocontext harness launches CLI trees (`uvx -> autoctx -> pi -> node`).
A plain `subprocess.run(..., timeout=...)` can leave descendants alive when only the
immediate child is interrupted. These helpers start each command in a new process
group, track active groups, and terminate the full group on timeout or parent
termination.
"""

from __future__ import annotations

import atexit
import os
import signal
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

_ACTIVE_PROCESS_GROUPS: set[int] = set()
_SIGNAL_HANDLERS_INSTALLED = False


def _terminate_process_group(pgid: int, *, sig: int = signal.SIGTERM) -> None:
    """Best-effort signal delivery to a process group."""

    if pgid <= 0 or pgid == os.getpgrp():
        return
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        return
    except PermissionError:
        return


def _cleanup_active_process_groups() -> None:
    for pgid in list(_ACTIVE_PROCESS_GROUPS):
        _terminate_process_group(pgid, sig=signal.SIGTERM)


def _signal_cleanup(signum: int, _frame: Any) -> None:
    _cleanup_active_process_groups()
    raise SystemExit(128 + signum)


def install_process_group_cleanup() -> None:
    """Install atexit and termination-signal cleanup once per process."""

    global _SIGNAL_HANDLERS_INSTALLED
    if _SIGNAL_HANDLERS_INSTALLED:
        return
    _SIGNAL_HANDLERS_INSTALLED = True
    atexit.register(_cleanup_active_process_groups)
    try:
        signal.signal(signal.SIGTERM, _signal_cleanup)
        signal.signal(signal.SIGINT, _signal_cleanup)
    except ValueError:
        # Signal handlers can only be installed from the main thread. The harness
        # entry points run in the main thread, but keeping this defensive makes the
        # helper safe to import in tests or embedded callers.
        pass


def popen_process_group(
    cmd: Sequence[str],
    *,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
    text: bool = True,
    stdout: int | None = subprocess.PIPE,
    stderr: int | None = subprocess.PIPE,
) -> subprocess.Popen[str]:
    """Start a subprocess in a new session/process group and track it."""

    install_process_group_cleanup()
    proc = subprocess.Popen(
        list(cmd),
        cwd=cwd,
        env=dict(env) if env is not None else None,
        text=text,
        stdout=stdout,
        stderr=stderr,
        start_new_session=True,
    )
    _ACTIVE_PROCESS_GROUPS.add(proc.pid)
    return proc


def reap_process_group(proc: subprocess.Popen[str]) -> None:
    """Forget a process group and terminate any lingering descendants."""

    pgid = proc.pid
    _ACTIVE_PROCESS_GROUPS.discard(pgid)
    _terminate_process_group(pgid, sig=signal.SIGTERM)


def communicate_process_group(
    proc: subprocess.Popen[str],
    *,
    timeout: float,
    kill_grace: float = 10,
    timeout_marker: str = "EXTERNAL_TIMEOUT",
) -> tuple[str, str, bool, int]:
    """Communicate with a tracked process group and kill the group on timeout.

    Returns `(stdout, stderr, timed_out, exit_code)`. If the outer timeout fires,
    `timeout_marker` is appended to stderr and exit code `124` is returned. The
    process group is untracked in all cases and any lingering descendants are sent
    SIGTERM after the immediate child exits.
    """

    stdout = ""
    stderr = ""
    timed_out = False
    exit_code = 124
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        exit_code = int(proc.returncode or 0)
        return stdout or "", stderr or "", False, exit_code
    except subprocess.TimeoutExpired:
        timed_out = True
        _terminate_process_group(proc.pid, sig=signal.SIGTERM)
        try:
            stdout, stderr = proc.communicate(timeout=kill_grace)
        except subprocess.TimeoutExpired:
            _terminate_process_group(proc.pid, sig=signal.SIGKILL)
            stdout, stderr = proc.communicate()
        stderr = (stderr or "") + f"\n{timeout_marker}\n"
        return stdout or "", stderr or "", timed_out, exit_code
    finally:
        reap_process_group(proc)
