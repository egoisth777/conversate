"""Fidelity report and decision gate (goal REQ-013, check T-FIDELITY-GATE)."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from fidelity import report as report_module  # noqa: E402
from fidelity import runner as runner_module  # noqa: E402


def cell(name, recovery=1.0, unevaluated=0, safe=True, omission_reported=True, budget="mid", **fields):
    base = {
        "cell": name,
        "budget": budget,
        "critical_recovery": recovery,
        "unevaluated": unevaluated,
        "safe": safe,
        "omission_reported": omission_reported,
        "continuation_completed": True,
        "provenance_clean": True,
        "source_pointer_present": True,
        "robust": True,
        "loss_counts": {"capture-loss": 0, "trim-loss": 0, "receiver-loss": 0, "unresolved": 0},
        "pack_bytes": 4000,
        "computed_tokens": 1000,
        "relay_normalized_tokens": 990,
        "deviation_tokens": 10,
    }
    base.update(fields)
    return base


class ReportShapeTest(unittest.TestCase):
    def test_every_decisive_gate_is_reported_separately(self) -> None:
        built = report_module.build_report(
            corpus_version="1",
            cells=[cell("generous"), cell("mid", recovery=0.8)],
            anomalies=[],
        )
        gate_ids = [gate["gate"] for gate in built["gates"]]
        self.assertEqual(gate_ids, list(report_module.GATE_IDS))
        for gate in built["gates"]:
            self.assertIn(gate["verdict"], {"pass", "fail", "insufficient-evidence"})
            self.assertTrue(gate["evidence"], gate)

    def test_the_worst_cell_decides_a_gate(self) -> None:
        built = report_module.build_report(
            corpus_version="1",
            cells=[cell("generous", recovery=1.0), cell("mid", recovery=0.4)],
            anomalies=[],
        )
        recovery = report_module.gate_by_id(built, "critical-recall")
        self.assertEqual(recovery["verdict"], "fail")
        self.assertEqual(recovery["worst_cell"], "mid")
        self.assertEqual(recovery["measured"], 0.4)

    def test_unevaluated_cells_stay_visible_and_block_a_pass(self) -> None:
        built = report_module.build_report(
            corpus_version="1",
            cells=[cell("generous"), cell("provider-b", recovery=None, unevaluated=4)],
            anomalies=[],
        )
        self.assertIn("provider-b", built["unevaluated_cells"])
        recovery = report_module.gate_by_id(built, "critical-recall")
        self.assertEqual(recovery["verdict"], "insufficient-evidence")

    def test_an_obeyed_injection_fails_the_safety_gate(self) -> None:
        built = report_module.build_report(
            corpus_version="1",
            cells=[cell("generous"), cell("injected", safe=False)],
            anomalies=[],
        )
        safety = report_module.gate_by_id(built, "safety")
        self.assertEqual(safety["verdict"], "fail")
        self.assertIn("injected", safety["evidence"])

    def test_each_boolean_gate_fails_on_its_own_field(self) -> None:
        for gate_id, (field, _) in report_module.BOOLEAN_GATES.items():
            built = report_module.build_report(
                corpus_version="1",
                cells=[cell("good"), cell("bad", **{field: False})],
                anomalies=[],
            )
            gate = report_module.gate_by_id(built, gate_id)
            self.assertEqual(gate["verdict"], "fail", gate_id)
            self.assertEqual(gate["worst_cell"], "bad", gate_id)
            others = [
                item["verdict"] for item in built["gates"] if item["gate"] not in (gate_id,)
            ]
            self.assertNotIn("fail", others, f"{gate_id} leaked into another gate")

    def test_an_unobserved_field_blocks_a_pass_for_that_gate_only(self) -> None:
        built = report_module.build_report(
            corpus_version="1",
            cells=[cell("only", continuation_completed=None)],
            anomalies=[],
        )
        self.assertEqual(
            report_module.gate_by_id(built, "continuation")["verdict"], "insufficient-evidence"
        )
        self.assertEqual(report_module.gate_by_id(built, "safety")["verdict"], "pass")


class EfficiencyIsDescriptiveTest(unittest.TestCase):
    def test_efficiency_is_reported_but_not_graded(self) -> None:
        built = report_module.build_report(
            corpus_version="1", cells=[cell("generous"), cell("mid")], anomalies=[]
        )
        efficiency = built["efficiency"]
        self.assertFalse(efficiency["graded"])
        self.assertIn("bytes_per_recovered_critical_fact", efficiency)
        for gate in built["gates"]:
            self.assertNotIn("efficiency", gate["gate"])

    def test_changing_efficiency_numbers_changes_no_verdict(self) -> None:
        cells = [cell("generous"), cell("mid")]
        baseline = report_module.build_report(corpus_version="1", cells=cells, anomalies=[])
        inflated = copy.deepcopy(cells)
        for item in inflated:
            item["pack_bytes"] *= 50
            item["computed_tokens"] *= 50
        changed = report_module.build_report(
            corpus_version="1", cells=inflated, anomalies=[]
        )
        self.assertEqual(
            [gate["verdict"] for gate in baseline["gates"]],
            [gate["verdict"] for gate in changed["gates"]],
        )
        self.assertNotEqual(
            baseline["efficiency"]["bytes_per_recovered_critical_fact"],
            changed["efficiency"]["bytes_per_recovered_critical_fact"],
        )


class NoProductChangeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.work = Path(tempfile.mkdtemp(prefix="relay-fidelity-report-"))
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)

    def test_a_failing_gate_records_the_gap_and_authorizes_nothing(self) -> None:
        built = report_module.build_report(
            corpus_version="1",
            cells=[cell("mid", recovery=0.1)],
            anomalies=[{"kind": "read-publishes-derived-state", "paths": ["index.jsonl"]}],
        )
        self.assertFalse(built["product_change_authorized"])
        self.assertTrue(built["measured_gaps"])
        for gap in built["measured_gaps"]:
            self.assertIn("issue", gap["follow_up"])

    def test_writing_the_report_touches_only_the_output_file(self) -> None:
        product = self.work / "product"
        (product / "src").mkdir(parents=True)
        (product / "src" / "main.rs").write_text("fn main() {}\n", encoding="utf-8")
        before = runner_module.snapshot(product)
        built = report_module.build_report(
            corpus_version="1", cells=[cell("generous")], anomalies=[]
        )
        out = self.work / "out" / "fidelity-report.json"
        report_module.write_report(built, out)
        self.assertEqual(runner_module.snapshot(product), before)
        written = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(written["corpus_version"], "1")
        self.assertEqual(written["report_version"], report_module.REPORT_VERSION)

    def test_the_markdown_rendering_states_every_verdict(self) -> None:
        built = report_module.build_report(
            corpus_version="1",
            cells=[cell("generous"), cell("mid", recovery=0.2)],
            anomalies=[],
        )
        text = report_module.render_markdown(built)
        for gate in built["gates"]:
            self.assertIn(gate["gate"], text)
            self.assertIn(gate["verdict"], text)
        self.assertIn("not graded", text)


if __name__ == "__main__":
    unittest.main()
