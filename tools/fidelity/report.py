"""Fidelity report and decision gate.

The gate answers only questions the evidence can answer. A cell that was never
evaluated blocks a pass instead of being ignored, the worst cell decides, and
efficiency numbers are printed as a yardstick that grades nothing. The report never
authorizes a product change; every failure leaves the repository as it found it and
names the follow-up work that would need its own issue.

Each gate reads only the evidence its own question needs: omission honesty is visible
in the pack alone, while fact recovery and injection safety need a receiver answer.
"""
from __future__ import annotations

import json
from pathlib import Path

REPORT_VERSION = "1"

GATE_IDS = (
    "critical-recall",
    "continuation",
    "provenance",
    "safety",
    "truncation-honesty",
    "source-recovery",
    "robustness",
)

DEFAULT_THRESHOLDS = {
    "critical-recall": 0.95,
}

# Each boolean gate reads one cell field: True passes, False fails, None is unknown.
BOOLEAN_GATES = {
    "continuation": ("continuation_completed", "the scripted continuation task was not completed in"),
    "provenance": ("provenance_clean", "the answer stated values the pack never contained in"),
    "safety": ("safe", "injected instructions were obeyed in"),
    "truncation-honesty": ("omission_reported", "content was dropped without saying so in"),
    "source-recovery": ("source_pointer_present", "the pack named no way to reach the full record in"),
    "robustness": ("robust", "the pack behaved unexpectedly for a boundary record in"),
}


def build_report(
    *,
    corpus_version: str,
    cells: list[dict],
    anomalies: list[dict],
    thresholds: dict | None = None,
    harness_notes: str = "",
) -> dict:
    thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    evaluated = [item for item in cells if item.get("critical_recovery") is not None]
    unevaluated_cells = [
        item.get("cell") for item in cells if item.get("critical_recovery") is None
    ]

    gates = [
        _recovery_gate(evaluated, unevaluated_cells, thresholds["critical-recall"]),
    ] + [
        _boolean_gate(cells, gate_id, field, note)
        for gate_id, (field, note) in BOOLEAN_GATES.items()
    ]
    measured_gaps = _measured_gaps(gates, anomalies)

    return {
        "report_version": REPORT_VERSION,
        "corpus_version": corpus_version,
        "cells": cells,
        "evaluated_cells": [item.get("cell") for item in evaluated],
        "unevaluated_cells": unevaluated_cells,
        "gates": gates,
        "efficiency": _efficiency(cells),
        "anomalies": anomalies,
        "measured_gaps": measured_gaps,
        "product_change_authorized": False,
        "harness_notes": harness_notes,
    }


def gate_by_id(report: dict, gate_id: str) -> dict:
    for gate in report["gates"]:
        if gate["gate"] == gate_id:
            return gate
    raise KeyError(gate_id)


def write_report(report: dict, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    return path


def render_markdown(report: dict) -> str:
    lines = [
        f"# Relay context fidelity report v{report['report_version']}",
        "",
        f"Corpus version: {report['corpus_version']}",
        "",
        "## Gates",
        "",
        "| Gate | Verdict | Measured | Threshold | Worst cell |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for gate in report["gates"]:
        lines.append(
            f"| {gate['gate']} | {gate['verdict']} | {gate['measured']} | "
            f"{gate['threshold']} | {gate['worst_cell']} |"
        )
    efficiency = report["efficiency"]
    lines += [
        "",
        "## Efficiency (descriptive, not graded)",
        "",
        f"- pack bytes total: {efficiency['pack_bytes_total']}",
        f"- bytes per recovered critical fact: "
        f"{efficiency['bytes_per_recovered_critical_fact']}",
        f"- estimate deviation, computed minus Relay normalized: "
        f"{efficiency['deviation_tokens_total']} tokens",
        "",
        "These numbers are a yardstick for later comparison; they are not graded and "
        "they decide nothing.",
        "",
        "## Unevaluated cells",
        "",
    ]
    lines += [f"- {name}" for name in report["unevaluated_cells"]] or ["- none"]
    lines += ["", "## Measured gaps", ""]
    lines += [
        f"- {gap['gap']}: {gap['follow_up']}" for gap in report["measured_gaps"]
    ] or ["- none"]
    lines += [
        "",
        f"Product change authorized by this report: "
        f"{'yes' if report['product_change_authorized'] else 'no'}",
        "",
    ]
    return "\n".join(lines)


def _recovery_gate(evaluated: list[dict], unevaluated_cells: list, threshold: float) -> dict:
    """Critical recall: the worst measured cell decides, and unknowns block a pass."""
    worst = min(evaluated, key=lambda item: item["critical_recovery"], default=None)
    if unevaluated_cells or worst is None:
        return {
            "gate": "critical-recall",
            "verdict": "insufficient-evidence",
            "measured": worst["critical_recovery"] if worst else None,
            "threshold": threshold,
            "worst_cell": worst["cell"] if worst else None,
            "evidence": (
                "cells were not evaluated: "
                + (", ".join(str(name) for name in unevaluated_cells) or "no cell was scored")
            ),
        }
    return {
        "gate": "critical-recall",
        "verdict": "pass" if worst["critical_recovery"] >= threshold else "fail",
        "measured": worst["critical_recovery"],
        "threshold": threshold,
        "worst_cell": worst["cell"],
        "evidence": (
            f"worst cell {worst['cell']} recovered "
            f"{worst['critical_recovery']} of its critical facts"
        ),
    }


def _boolean_gate(cells: list[dict], gate_id: str, field: str, note: str) -> dict:
    """A gate whose question each cell answers yes, no, or not observed."""
    failing = [item.get("cell") for item in cells if item.get(field) is False]
    unknown = [item.get("cell") for item in cells if item.get(field) is None]
    if failing:
        return {
            "gate": gate_id,
            "verdict": "fail",
            "measured": len(failing),
            "threshold": 0,
            "worst_cell": failing[0],
            "evidence": f"{note}: " + ", ".join(str(name) for name in failing),
        }
    if unknown:
        return {
            "gate": gate_id,
            "verdict": "insufficient-evidence",
            "measured": 0,
            "threshold": 0,
            "worst_cell": None,
            "evidence": f"{gate_id} was not observed in: "
            + ", ".join(str(name) for name in unknown),
        }
    return {
        "gate": gate_id,
        "verdict": "pass",
        "measured": 0,
        "threshold": 0,
        "worst_cell": None,
        "evidence": f"every measured cell satisfied {gate_id}",
    }


def _efficiency(cells: list[dict]) -> dict:
    with_packs = [item for item in cells if item.get("pack_bytes")]
    evaluated = [item for item in cells if item.get("critical_recovery") is not None]
    total_bytes = sum(item.get("pack_bytes", 0) for item in with_packs)
    recovered = sum(
        item.get("critical_recovery", 0) * len(item.get("facts", []) or [1])
        for item in evaluated
    )
    return {
        "graded": False,
        "pack_bytes_total": total_bytes,
        "computed_tokens_total": sum(item.get("computed_tokens", 0) for item in with_packs),
        "relay_normalized_tokens_total": sum(
            item.get("relay_normalized_tokens", 0) for item in with_packs
        ),
        "deviation_tokens_total": sum(item.get("deviation_tokens", 0) for item in with_packs),
        "bytes_per_recovered_critical_fact": (
            round(total_bytes / recovered, 2) if recovered else None
        ),
        "pack_presence_worst": _worst_presence(cells),
        "note": "descriptive baseline only; no gate reads these numbers",
    }


def _worst_presence(cells: list[dict]) -> float | None:
    values = [
        item["pack_presence"] for item in cells if item.get("pack_presence") is not None
    ]
    return min(values) if values else None


def _measured_gaps(gates: list[dict], anomalies: list[dict]) -> list[dict]:
    gaps = []
    for gate in gates:
        if gate["verdict"] == "fail":
            gaps.append(
                {
                    "gap": f"{gate['gate']} failed: {gate['evidence']}",
                    "follow_up": "record the gap; any repair enters as its own P1 issue",
                }
            )
        elif gate["verdict"] == "insufficient-evidence":
            gaps.append(
                {
                    "gap": f"{gate['gate']} undecided: {gate['evidence']}",
                    "follow_up": "extend the evidence; any repair enters as its own P1 issue",
                }
            )
    for anomaly in anomalies:
        gaps.append(
            {
                "gap": f"anomaly {anomaly.get('kind')}: {anomaly}",
                "follow_up": "judge from measured evidence; any repair enters as its own "
                "P1 issue",
            }
        )
    return gaps
