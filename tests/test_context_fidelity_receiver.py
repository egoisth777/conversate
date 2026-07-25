"""Receiver adapter behavior (goal REQ-012, check T-FIDELITY-RUN)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))
from fidelity import receiver as receiver_module  # noqa: E402

CONFIG = {
    "receivers": [
        {
            "name": "provider-a",
            "provider": "provider-a",
            "model": "model-a",
            "host": "api.provider-a.test",
            "credential_env": "RELAY_FIDELITY_A_KEY",
        },
        {
            "name": "provider-b",
            "provider": "provider-b",
            "model": "model-b",
            "host": "api.provider-b.test",
            "credential_env": "RELAY_FIDELITY_B_KEY",
        },
    ]
}


class UnconfiguredTest(unittest.TestCase):
    def test_without_credentials_every_provider_case_is_unevaluated(self) -> None:
        receivers = receiver_module.load_receivers(CONFIG, env={})
        self.assertEqual(len(receivers), 2)
        for entry in receivers:
            self.assertFalse(entry.available)
            result = entry.run(pack_text="pack", task="say the tag")
            self.assertEqual(result["status"], "unevaluated")
            self.assertIsNone(result["answer"])
            self.assertFalse(result["passed"])
            self.assertIn("credential", result["reason"])

    def test_an_unevaluated_result_scores_as_unresolved_not_as_a_miss(self) -> None:
        from fidelity import scoring

        entry = receiver_module.load_receivers(CONFIG, env={})[0]
        result = entry.run(pack_text="release tag v2.4.0", task="say the tag")
        scored = scoring.score_case(
            gold_facts=[{"kind": "version", "value": "v2.4.0", "source": "record:qa"}],
            record_text="release tag v2.4.0",
            pack_text="release tag v2.4.0",
            answer_text=result["answer"],
            cell="provider-a",
        )
        self.assertIsNone(scored["critical_recovery"])
        self.assertEqual(scored["loss_counts"]["unresolved"], 1)


class StubTransportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.calls = []

        def transport(request):
            self.calls.append(request)
            return {
                "answer": "The tag is v2.4.0.",
                "input_tokens": 128,
                "output_tokens": 9,
            }

        self.transport = transport
        self.env = {"RELAY_FIDELITY_A_KEY": "sk-secret-value-000111222"}

    def test_telemetry_is_recorded_for_a_configured_receiver(self) -> None:
        entry = receiver_module.load_receivers(
            CONFIG, env=self.env, transport=self.transport
        )[0]
        self.assertTrue(entry.available)
        result = entry.run(pack_text="release tag v2.4.0", task="say the tag")
        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(result["answer"], "The tag is v2.4.0.")
        telemetry = result["telemetry"]
        for field in ("provider", "model", "host", "input_tokens", "retries", "intervention"):
            self.assertIn(field, telemetry)
        self.assertEqual(telemetry["provider"], "provider-a")
        self.assertEqual(telemetry["input_tokens"], 128)
        self.assertEqual(telemetry["retries"], 0)
        self.assertFalse(telemetry["intervention"])

    def test_the_credential_never_appears_in_a_recorded_field(self) -> None:
        entry = receiver_module.load_receivers(
            CONFIG, env=self.env, transport=self.transport
        )[0]
        result = entry.run(pack_text="release tag v2.4.0", task="say the tag")
        blob = repr(result)
        self.assertNotIn("sk-secret-value-000111222", blob)
        self.assertNotIn("sk-secret-value-000111222", repr(entry.describe()))

    def test_retries_and_intervention_are_counted(self) -> None:
        attempts = {"n": 0}

        def flaky(request):
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise TimeoutError("transport stalled")
            return {"answer": "recovered", "input_tokens": 10, "intervention": True}

        entry = receiver_module.load_receivers(CONFIG, env=self.env, transport=flaky)[0]
        result = entry.run(pack_text="pack", task="task")
        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(result["telemetry"]["retries"], 2)
        self.assertTrue(result["telemetry"]["intervention"])

    def test_exhausted_retries_stay_unevaluated_rather_than_failing_the_receiver(self) -> None:
        def always_failing(request):
            raise TimeoutError("transport stalled")

        entry = receiver_module.load_receivers(
            CONFIG, env=self.env, transport=always_failing
        )[0]
        result = entry.run(pack_text="pack", task="task")
        self.assertEqual(result["status"], "unevaluated")
        self.assertIsNone(result["answer"])
        self.assertFalse(result["passed"])
        self.assertIn("transport", result["reason"])

    def test_the_raw_context_baseline_is_run_beside_the_pack(self) -> None:
        entry = receiver_module.load_receivers(
            CONFIG, env=self.env, transport=self.transport
        )[0]
        pair = receiver_module.run_with_baseline(
            entry, pack_text="pack text", raw_text="raw record text", task="task"
        )
        self.assertEqual(set(pair), {"pack", "raw_baseline"})
        sent = [call["context"] for call in self.calls]
        self.assertIn("pack text", sent)
        self.assertIn("raw record text", sent)


if __name__ == "__main__":
    unittest.main()
