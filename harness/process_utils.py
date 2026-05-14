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
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

_ACTIVE_PROCESS_GROUPS: set[int] = set()
_SIGNAL_HANDLERS_INSTALLED = False
_EXIT_CLEANUP_GRACE_SECONDS = 1.0
_DEFAULT_SIGKILL_GRACE_SECONDS = 1.0
_DEFAULT_PIPE_CLOSE_GRACE_SECONDS = 1.0


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
    pgids = list(_ACTIVE_PROCESS_GROUPS)
    for pgid in pgids:
        _terminate_process_group(pgid, sig=signal.SIGTERM)
    if not pgids:
        return
    time.sleep(_EXIT_CLEANUP_GRACE_SECONDS)
    for pgid in pgids:
        _terminate_process_group(pgid, sig=signal.SIGKILL)


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


def _decode_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _prefer_timeout_output(current: str, partial: str | bytes | None) -> str:
    decoded = _decode_output(partial)
    if not decoded:
        return current or ""
    if not current or len(decoded) >= len(current):
        return decoded
    return current


def _capture_timeout_output(
    stdout: str,
    stderr: str,
    exc: subprocess.TimeoutExpired,
) -> tuple[str, str]:
    """Preserve partial communicate output from a TimeoutExpired exception."""

    return (
        _prefer_timeout_output(stdout, exc.output),
        _prefer_timeout_output(stderr, exc.stderr),
    )


def _close_process_pipes(proc: subprocess.Popen[str]) -> None:
    """Force-close stdout/stderr pipes so communicate cannot wait on leaked FDs."""

    for pipe in (proc.stdout, proc.stderr):
        if pipe is None:
            continue
        try:
            pipe.close()
        except OSError:
            pass
        except ValueError:
            pass


def _kill_immediate_child(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.kill()
    except ProcessLookupError:
        return


def communicate_process_group(
    proc: subprocess.Popen[str],
    *,
    timeout: float,
    kill_grace: float = 10,
    sigkill_grace: float | None = None,
    pipe_close_grace: float = _DEFAULT_PIPE_CLOSE_GRACE_SECONDS,
    timeout_marker: str = "EXTERNAL_TIMEOUT",
) -> tuple[str, str, bool, int]:
    """Communicate with a tracked process group and kill the group on timeout.

    Returns `(stdout, stderr, timed_out, exit_code)`. If the outer timeout fires,
    `timeout_marker` is appended to stderr and exit code `124` is returned. Timeout
    cleanup is bounded: after SIGTERM and SIGKILL grace periods, stdout/stderr pipe
    handles are force-closed so escaped descendants or leaked file descriptors
    cannot keep `communicate()` blocked indefinitely. The process group is
    untracked in all cases and any lingering in-group descendants are sent SIGTERM
    after the immediate child exits.
    """

    stdout = ""
    stderr = ""
    timed_out = False
    exit_code = 124
    effective_sigkill_grace = (
        sigkill_grace
        if sigkill_grace is not None
        else min(kill_grace, _DEFAULT_SIGKILL_GRACE_SECONDS)
    )
    try:
        raw_stdout, raw_stderr = proc.communicate(timeout=timeout)
        stdout = _decode_output(raw_stdout)
        stderr = _decode_output(raw_stderr)
        exit_code = int(proc.returncode or 0)
        return stdout, stderr, False, exit_code
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout, stderr = _capture_timeout_output(stdout, stderr, exc)
        _terminate_process_group(proc.pid, sig=signal.SIGTERM)
        try:
            raw_stdout, raw_stderr = proc.communicate(timeout=kill_grace)
            stdout = _decode_output(raw_stdout)
            stderr = _decode_output(raw_stderr)
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = _capture_timeout_output(stdout, stderr, exc)
            _terminate_process_group(proc.pid, sig=signal.SIGKILL)
            try:
                raw_stdout, raw_stderr = proc.communicate(timeout=effective_sigkill_grace)
                stdout = _decode_output(raw_stdout)
                stderr = _decode_output(raw_stderr)
            except subprocess.TimeoutExpired as exc:
                stdout, stderr = _capture_timeout_output(stdout, stderr, exc)
                _close_process_pipes(proc)
                _kill_immediate_child(proc)
                try:
                    proc.wait(timeout=pipe_close_grace)
                except subprocess.TimeoutExpired:
                    pass
        stderr = (stderr or "") + f"\n{timeout_marker}\n"
        return stdout or "", stderr or "", timed_out, exit_code
    finally:
        reap_process_group(proc)
