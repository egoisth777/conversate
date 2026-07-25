"""Corpus validation for the context-fidelity harness (goal REQ-012, check T-FIDELITY-CORPUS)."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from fidelity import corpus as corpus_module  # noqa: E402


def gold_fact(kind: str = "path", value: str = "src/main.rs") -> dict:
    return {"kind": kind, "value": value, "source": "record:summary", "critical": True}


def held_out(index: int) -> dict:
    return {
        "reference": f"held-out-{index}",
        "record_id": f"redacted-{index}",
        "gold_facts": [gold_fact()],
        "continuation_task": "state the next command to run",
    }


def synthetic(boundary: str, fixture: str) -> dict:
    return {
        "reference": f"synthetic-{boundary}",
        "boundary": boundary,
        "fixture": fixture,
        "gold_facts": [gold_fact()],
        "continuation_task": "state the next command to run",
    }


class CorpusValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.base = Path(self.enterContext(__import__("tempfile").TemporaryDirectory()))
        self.fixtures = self.base / "fixtures"
        self.fixtures.mkdir()
        for boundary in corpus_module.REQUIRED_BOUNDARIES:
            (self.fixtures / f"{boundary}.md").write_text(
                f"# {boundary} fixture\n\nsummary line naming src/main.rs\n",
                encoding="utf-8",
            )

    def manifest(self, **overrides) -> dict:
        data = {
            "corpus_version": "1",
            "held_out_records": [held_out(index) for index in range(1, 6)],
            "synthetic_records": [
                synthetic(boundary, f"fixtures/{boundary}.md")
                for boundary in sorted(corpus_module.REQUIRED_BOUNDARIES)
            ],
            "budgets": list(corpus_module.REQUIRED_BUDGETS),
            "receivers": [
                {"provider": "provider-a", "model": "model-a", "host": "host-a"},
                {"provider": "provider-b", "model": "model-b", "host": "host-b"},
            ],
        }
        data.update(overrides)
        return data

    def test_complete_manifest_reports_no_problems(self) -> None:
        self.assertEqual(corpus_module.validate(self.manifest(), self.base), [])

    def test_too_few_held_out_records_is_reported(self) -> None:
        problems = corpus_module.validate(
            self.manifest(held_out_records=[held_out(1), held_out(2)]), self.base
        )
        self.assertTrue(any("held-out" in problem for problem in problems), problems)
        self.assertTrue(any("2" in problem and "5" in problem for problem in problems), problems)

    def test_missing_boundary_case_is_named(self) -> None:
        kept = [
            synthetic(boundary, f"fixtures/{boundary}.md")
            for boundary in sorted(corpus_module.REQUIRED_BOUNDARIES)
            if boundary != "injected-instructions"
        ]
        problems = corpus_module.validate(self.manifest(synthetic_records=kept), self.base)
        self.assertTrue(
            any("injected-instructions" in problem for problem in problems), problems
        )

    def test_a_gold_fact_absent_from_its_fixture_is_reported(self) -> None:
        records = [
            synthetic(boundary, f"fixtures/{boundary}.md")
            for boundary in sorted(corpus_module.REQUIRED_BOUNDARIES)
        ]
        records[0] = {**records[0], "gold_facts": [gold_fact(value="never written anywhere")]}
        problems = corpus_module.validate(self.manifest(synthetic_records=records), self.base)
        self.assertTrue(
            any("never written anywhere" in problem for problem in problems), problems
        )

    def test_missing_fixture_file_is_reported(self) -> None:
        (self.fixtures / "legacy-schema.md").unlink()
        problems = corpus_module.validate(self.manifest(), self.base)
        self.assertTrue(any("legacy-schema.md" in problem for problem in problems), problems)

    def test_inline_record_body_is_rejected(self) -> None:
        leaking = held_out(1)
        leaking["body"] = "private handoff content"
        records = [leaking] + [held_out(index) for index in range(2, 6)]
        problems = corpus_module.validate(self.manifest(held_out_records=records), self.base)
        self.assertTrue(any("body" in problem for problem in problems), problems)

    def test_secret_in_fixture_is_rejected(self) -> None:
        (self.fixtures / "legacy-schema.md").write_text(
            "token: sk-livetokenvalue0000000000\n", encoding="utf-8"
        )
        problems = corpus_module.validate(self.manifest(), self.base)
        self.assertTrue(any("secret" in problem for problem in problems), problems)

    def test_missing_gold_facts_are_reported(self) -> None:
        bare = held_out(1)
        bare["gold_facts"] = []
        records = [bare] + [held_out(index) for index in range(2, 6)]
        problems = corpus_module.validate(self.manifest(held_out_records=records), self.base)
        self.assertTrue(any("gold fact" in problem for problem in problems), problems)

    def test_incomplete_budget_set_is_reported(self) -> None:
        problems = corpus_module.validate(
            self.manifest(budgets=["generous", "mid"]), self.base
        )
        self.assertTrue(any("minimum-minus-one" in problem for problem in problems), problems)

    def test_single_receiver_is_reported(self) -> None:
        problems = corpus_module.validate(
            self.manifest(receivers=[{"provider": "a", "model": "m", "host": "h"}]),
            self.base,
        )
        self.assertTrue(any("receiver" in problem for problem in problems), problems)


class ShippedCorpusTest(unittest.TestCase):
    """The shipped corpus must load and must report its own gaps honestly."""

    def test_shipped_corpus_loads_and_states_its_gaps(self) -> None:
        path = REPO_ROOT / "tools" / "fidelity" / "corpus" / "corpus.json"
        data = corpus_module.load(path)
        problems = corpus_module.validate(data, path.parent)
        declared = data.get("known_gaps", [])
        self.assertTrue(declared, "an incomplete corpus must declare its gaps")
        for problem in problems:
            self.assertTrue(
                any(gap in problem for gap in declared),
                f"undeclared corpus problem: {problem}",
            )

    def test_shipped_corpus_commits_no_private_body(self) -> None:
        path = REPO_ROOT / "tools" / "fidelity" / "corpus" / "corpus.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        for record in raw.get("held_out_records", []):
            self.assertNotIn("body", record)


if __name__ == "__main__":
    unittest.main()
