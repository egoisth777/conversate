"""Installed-path proof that hook turn counting never loses a submission.

These tests drive the shipped `relay hook` command through subprocesses, so they
exercise the same lock, counter, and reminder protocol a real agent invokes.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _util import clean_env, run_cli  # noqa: E402

REMINDER = "RELAY HANDOFF"


def session_hash(session: str) -> int:
    value = 0
    for byte in session.encode("utf-8"):
        value = (value * 131 + byte) % (1 << 64)
    return value


def submit(home: Path, session: str, agent: str = "codex"):
    payload = json.dumps({"event": "UserPromptSubmit", "session_id": session})
    return run_cli(
        ["hook", "--agent", agent],
        cwd=home,
        env=clean_env(home=home),
        input=payload,
        timeout=60,
    )


def counter_path(home: Path, session: str) -> Path:
    state = home / ".relay" / ".semble" / "hook-state"
    return state / f"relay-hook-{session_hash(session)}.count"


class HookIncrementTest(unittest.TestCase):
    def setUp(self) -> None:
        self.home = Path(tempfile.mkdtemp(prefix="relay-hook-e2e-"))
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)

    def test_every_submission_counts_and_reminds_on_tenth_turns(self) -> None:
        session = "installed-sequential"
        reminders = []
        turns = 25
        for turn in range(1, turns + 1):
            proc = submit(self.home, session)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            if REMINDER in proc.stdout:
                reminders.append(turn)
        self.assertEqual(reminders, [10, 20])
        self.assertEqual(counter_path(self.home, session).read_text().strip(), str(turns))

    def test_concurrent_submissions_are_lossless(self) -> None:
        session = "installed-concurrent"
        workers = 16
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(lambda _: submit(self.home, session), range(workers)))
        for proc in results:
            self.assertEqual(proc.returncode, 0, proc.stderr)
        reminders = sum(1 for proc in results if REMINDER in proc.stdout)
        persisted = int(counter_path(self.home, session).read_text().strip())
        self.assertEqual(
            persisted,
            workers,
            f"lost submissions: persisted {persisted} of {workers}",
        )
        self.assertEqual(reminders, persisted // 10)

    def test_sessions_keep_separate_counters(self) -> None:
        first, second = "installed-alpha", "installed-beta"
        self.assertNotEqual(session_hash(first), session_hash(second))
        for _ in range(3):
            submit(self.home, first)
        submit(self.home, second)
        self.assertEqual(counter_path(self.home, first).read_text().strip(), "3")
        self.assertEqual(counter_path(self.home, second).read_text().strip(), "1")

    def test_rejected_input_writes_no_counter(self) -> None:
        state = self.home / ".relay" / ".semble" / "hook-state"
        proc = run_cli(
            ["hook", "--agent", "codex"],
            cwd=self.home,
            env=clean_env(home=self.home),
            input=json.dumps({"event": "SessionStart", "session_id": "ignored"}),
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn(REMINDER, proc.stdout)
        if state.is_dir():
            self.assertEqual(list(state.glob("*.count")), [])


if __name__ == "__main__":
    unittest.main()
