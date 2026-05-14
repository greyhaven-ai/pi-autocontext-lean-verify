#!/usr/bin/env python3
from __future__ import annotations

import os
import signal
import sys
import tempfile
import time
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
HARNESS = PACKAGE / "harness"
sys.path.insert(0, str(HARNESS))

from process_utils import _ACTIVE_PROCESS_GROUPS, communicate_process_group, popen_process_group, reap_process_group  # noqa: E402


class ProcessGroupCommunicationTests(unittest.TestCase):
    def test_timeout_returns_promptly_when_escaped_descendant_keeps_pipe_open(self) -> None:
        """Timeout cleanup must not block forever on inherited pipe handles.

        The child process launches a grandchild that creates a new session, keeps
        stdout/stderr inherited from the original process, and sleeps. Killing the
        original process group removes the tracked child but does not close the
        inherited pipe in the escaped descendant. communicate_process_group should
        force-close its pipe handles and return a timeout result promptly.
        """

        with tempfile.TemporaryDirectory(prefix="process-utils-pipe-leak-") as tmp:
            tmpdir = Path(tmp)
            pid_file = tmpdir / "escaped-child.pid"
            escaped_child_pid: int | None = None
            parent_code = r"""
import subprocess
import sys
import time

pid_file = sys.argv[1]
grandchild_code = r'''
import os
import sys
import time
from pathlib import Path

os.setsid()
Path(sys.argv[1]).write_text(str(os.getpid()), encoding="utf-8")
print("escaped-child-start", flush=True)
time.sleep(5)
'''
subprocess.Popen(
    [sys.executable, "-c", grandchild_code, pid_file],
    stdout=sys.stdout,
    stderr=sys.stderr,
    close_fds=False,
)
print("parent-start", flush=True)
time.sleep(30)
"""

            proc = popen_process_group([sys.executable, "-c", parent_code, str(pid_file)])
            try:
                deadline = time.monotonic() + 2
                while time.monotonic() < deadline and not pid_file.exists():
                    time.sleep(0.02)
                self.assertTrue(pid_file.exists(), "escaped child did not publish its PID")
                escaped_child_pid = int(pid_file.read_text(encoding="utf-8"))

                started = time.monotonic()
                stdout, stderr, timed_out, exit_code = communicate_process_group(
                    proc,
                    timeout=0.2,
                    kill_grace=0.2,
                    timeout_marker="PIPE_LEAK_TIMEOUT",
                )
                elapsed = time.monotonic() - started

                self.assertTrue(timed_out)
                self.assertEqual(exit_code, 124)
                self.assertIn("PIPE_LEAK_TIMEOUT", stderr)
                self.assertIn("parent-start", stdout)
                self.assertLess(elapsed, 2.0, f"timeout cleanup blocked on leaked pipe for {elapsed:.2f}s")
                self.assertNotIn(proc.pid, _ACTIVE_PROCESS_GROUPS)
            finally:
                if escaped_child_pid is not None:
                    try:
                        os.kill(escaped_child_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                reap_process_group(proc)


if __name__ == "__main__":
    unittest.main()
