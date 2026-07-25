"""Disposable-root measurement runner (goal REQ-012, check T-FIDELITY-RUN)."""
from __future__ import annotations

import math
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tests"))
from _util import RUST_BINARY  # noqa: E402
from fidelity import runner as runner_module  # noqa: E402

FIXTURE = REPO_ROOT / "tools" / "fidelity" / "corpus" / "fixtures" / "oversized-optional.md"
RECORD_ID = "fx-oversized-optional"


class RunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        if not RUST_BINARY.is_file():
            self.skipTest("relay binary is not built")
        self.work = Path(tempfile.mkdtemp(prefix="relay-fidelity-"))
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.source = self.work / "source-root"
        (self.source / "convs").mkdir(parents=True)
        shutil.copy(FIXTURE, self.source / "convs" / FIXTURE.name)

    def measure(self):
        return runner_module.measure_record(
            binary=RUST_BINARY,
            source_root=self.source,
            record_id=RECORD_ID,
            workdir=self.work / "run",
        )

    def test_source_installation_is_byte_identical_afterwards(self) -> None:
        before = runner_module.snapshot(self.source)
        report = self.measure()
        after = runner_module.snapshot(self.source)
        self.assertEqual(before, after, "measurement must not touch the source installation")
        self.assertEqual(report["source_installation"]["changed"], [])

    def test_a_cold_read_publishes_derived_state_and_it_is_reported(self) -> None:
        report = self.measure()
        self.assertTrue(
            any(
                "index-v2" in path or path.endswith("index.jsonl")
                for path in report["cold_read_derived_writes"]
            ),
            "a cold read published no derived state, which contradicts the observed "
            f"behavior: {report['cold_read_derived_writes']}",
        )
        kinds = {anomaly["kind"] for anomaly in report["anomalies"]}
        self.assertIn("read-publishes-derived-state", kinds)

    def test_every_budget_case_is_measured(self) -> None:
        report = self.measure()
        labels = [case["budget_label"] for case in report["cases"]]
        self.assertEqual(labels, list(runner_module.BUDGET_LABELS))

    def test_pack_metrics_are_recorded_for_every_accepted_case(self) -> None:
        report = self.measure()
        accepted = [case for case in report["cases"] if case["exit_code"] == 0]
        self.assertTrue(accepted, "no budget case produced a pack")
        for case in accepted:
            self.assertGreater(case["pack_bytes"], 0, case)
            self.assertEqual(
                case["computed_tokens"],
                math.ceil(case["pack_bytes"] / 4),
                "the independently computed estimate must be ceil(pack bytes / 4)",
            )
            self.assertIn(case["truncated"], {"yes", "no"})
            self.assertGreaterEqual(case["latency_ms"], 0)
            self.assertEqual(
                case["deviation_tokens"],
                case["computed_tokens"] - case["relay_normalized_tokens"],
                "the deviation between both token figures must be recorded, not implied",
            )
            self.assertGreaterEqual(
                case["deviation_tokens"],
                0,
                "Relay's root-normalized estimate cannot exceed the emitted pack",
            )


    def test_rejected_cases_carry_the_refusal_text(self) -> None:
        report = self.measure()
        rejected = [case for case in report["cases"] if case["exit_code"] != 0]
        self.assertTrue(
            any(case["budget_label"] == "minimum-minus-one" for case in rejected),
            "a budget below the reported minimum must be refused",
        )
        for case in rejected:
            self.assertIn("budget is too small", case["stderr"] + case["stdout"], case)
        self.assertEqual(report["records"]["changed"], [])

    def test_the_reported_minimum_is_checked_against_the_accepted_one(self) -> None:
        report = self.measure()
        kinds = {anomaly["kind"] for anomaly in report["anomalies"]}
        if report["smallest_accepted_budget"] == report["minimum_tokens"]:
            self.assertNotIn("reported-minimum-understates-accepted-budget", kinds)
            return
        self.assertGreater(report["smallest_accepted_budget"], report["minimum_tokens"])
        self.assertIn(
            "reported-minimum-understates-accepted-budget",
            kinds,
            "a reported minimum the tool then refuses is a measured gap and must be reported",
        )

    def test_budget_cases_are_planned_from_the_accepted_minimum(self) -> None:
        report = self.measure()
        accepted = report["smallest_accepted_budget"]
        by_label = {case["budget_label"]: case for case in report["cases"]}
        self.assertEqual(by_label["minimum-plus-one"]["budget_tokens"], accepted + 1)
        self.assertEqual(by_label["minimum-minus-one"]["budget_tokens"], accepted - 1)
        self.assertEqual(by_label["minimum-plus-one"]["exit_code"], 0)
        self.assertNotEqual(by_label["minimum-minus-one"]["exit_code"], 0)

    def test_a_broken_neighbor_record_is_probed_separately(self) -> None:
        fixtures = REPO_ROOT / "tools" / "fidelity" / "corpus" / "fixtures"
        probe = runner_module.measure_neighbor_contamination(
            binary=RUST_BINARY,
            healthy_record=fixtures / "mixed-weights.md",
            broken_record=fixtures / "malformed-link.md",
            healthy_id="fx-mixed-weights",
            workdir=self.work / "contamination",
        )
        self.assertEqual(probe["alone_exit_code"], 0)
        if probe["blocked"]:
            self.assertEqual(probe["anomaly"]["kind"], "broken-neighbor-blocks-healthy-record")
            self.assertTrue(probe["message"])

    def test_records_and_status_are_unchanged_in_the_disposable_root(self) -> None:
        report = self.measure()
        self.assertEqual(report["records"]["changed"], [])
        self.assertEqual(report["records"]["removed"], [])
        self.assertEqual(report["status_before"], report["status_after"])

    def test_reported_minimum_budget_is_discovered(self) -> None:
        report = self.measure()
        self.assertIsInstance(report["minimum_tokens"], int)
        self.assertGreater(report["minimum_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
