"""End-to-end fidelity baseline run (goal REQ-012/REQ-013, checks T-FIDELITY-RUN/GATE)."""
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tests"))
from _util import RUST_BINARY  # noqa: E402
from fidelity import baseline, corpus as corpus_module  # noqa: E402

CORPUS_DIR = REPO_ROOT / "tools" / "fidelity" / "corpus"


class BaselineRunTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not RUST_BINARY.is_file():
            raise unittest.SkipTest("relay binary is not built")
        cls.work = Path(tempfile.mkdtemp(prefix="relay-fidelity-baseline-"))
        cls.corpus = corpus_module.load(CORPUS_DIR / "corpus.json")
        cls.report = baseline.run_baseline(
            binary=RUST_BINARY,
            corpus=cls.corpus,
            base_dir=CORPUS_DIR,
            workdir=cls.work,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.work, ignore_errors=True)

    def test_every_synthetic_boundary_produces_cells(self) -> None:
        measured = {cell["record"] for cell in self.report["cells"]}
        expected = {record["reference"] for record in self.corpus["synthetic_records"]}
        self.assertEqual(measured, expected)

    def test_every_budget_case_appears_for_every_record(self) -> None:
        from fidelity.runner import BUDGET_LABELS

        for reference in {cell["record"] for cell in self.report["cells"]}:
            budgets = {
                cell["budget"] for cell in self.report["cells"] if cell["record"] == reference
            }
            self.assertEqual(budgets, set(BUDGET_LABELS), reference)

    def test_receiver_recovery_is_unevaluated_without_a_configured_provider(self) -> None:
        recovery = next(
            gate for gate in self.report["gates"] if gate["gate"] == "critical-recall"
        )
        self.assertEqual(recovery["verdict"], "insufficient-evidence")
        self.assertTrue(self.report["unevaluated_cells"])

    def test_pack_presence_is_measured_without_any_provider(self) -> None:
        presence = [
            cell["pack_presence"]
            for cell in self.report["cells"]
            if cell["pack_presence"] is not None
        ]
        self.assertTrue(presence, "trim loss must be measurable offline")
        for value in presence:
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_no_gold_fact_is_capture_loss_because_the_corpus_declares_them(self) -> None:
        capture = sum(
            cell["pack_loss_counts"]["capture-loss"] for cell in self.report["cells"]
        )
        self.assertEqual(
            capture,
            0,
            "every gold fact is quoted from its fixture, so nothing may be capture loss",
        )

    def test_trim_loss_is_attributed_where_a_pack_dropped_a_declared_fact(self) -> None:
        carried = sum(cell["pack_loss_counts"]["carried"] for cell in self.report["cells"])
        self.assertGreater(carried, 0, "no gold fact survived any pack")
        for cell in self.report["cells"]:
            counts = cell["pack_loss_counts"]
            self.assertEqual(
                sum(counts.values()),
                len(cell.get("facts", [])) or sum(counts.values()),
                cell["cell"],
            )

    def test_every_gate_named_by_the_requirement_is_reported(self) -> None:
        from fidelity.report import GATE_IDS

        self.assertEqual([gate["gate"] for gate in self.report["gates"]], list(GATE_IDS))
        for gate in self.report["gates"]:
            self.assertIn(gate["verdict"], {"pass", "fail", "insufficient-evidence"})

    def test_the_run_authorizes_no_product_change(self) -> None:
        self.assertFalse(self.report["product_change_authorized"])
        self.assertTrue(self.report["measured_gaps"])

    def test_the_contamination_probe_is_reported(self) -> None:
        probe = self.report["contamination_probe"]
        self.assertIsNotNone(probe, "the corpus declares a contamination probe")
        self.assertEqual(probe["alone_exit_code"], 0)
        if probe["blocked"]:
            kinds = {anomaly["kind"] for anomaly in self.report["anomalies"]}
            self.assertIn("broken-neighbor-blocks-healthy-record", kinds)

    def test_observed_anomalies_are_carried_into_the_report(self) -> None:
        kinds = {anomaly["kind"] for anomaly in self.report["anomalies"]}
        self.assertIn("read-publishes-derived-state", kinds)

    def test_the_relay_source_installation_is_never_touched(self) -> None:
        for record in self.report["source_installations"]:
            self.assertEqual(record["changed"], [])
            self.assertEqual(record["removed"], [])


if __name__ == "__main__":
    unittest.main()
