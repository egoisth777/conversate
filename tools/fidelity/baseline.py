"""Drive one full fidelity baseline: corpus -> disposable roots -> scoring -> report.

Receiver evidence is optional. Without a configured provider, fact recovery stays
`unevaluated` and only the pack-side questions - what survived the trim and whether the
pack admitted dropping content - are answered. Nothing here changes Relay.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import receiver as receiver_module
from . import report as report_module
from . import runner as runner_module
from . import scoring

_ID_PATTERN = re.compile(r'^id\s*=\s*"([^"]+)"', re.M)


def run_baseline(
    *,
    binary: Path,
    corpus: dict,
    base_dir: Path,
    workdir: Path,
    receivers: list | None = None,
) -> dict:
    base_dir = Path(base_dir)
    workdir = Path(workdir)
    receivers = receivers or []

    cells: list[dict] = []
    anomalies: list[dict] = []
    source_installations: list[dict] = []

    for entry in corpus.get("synthetic_records", []):
        reference = entry["reference"]
        fixture = base_dir / entry["fixture"]
        record_text = fixture.read_text(encoding="utf-8")
        match = _ID_PATTERN.search(record_text)
        if not match:
            cells.append(_unmeasurable_cell(reference, "fixture declares no record id"))
            continue
        record_id = match.group(1)

        source_root = workdir / reference / "source-root"
        (source_root / "convs").mkdir(parents=True, exist_ok=True)
        (source_root / "convs" / fixture.name).write_text(record_text, encoding="utf-8")
        for link in entry.get("link_fixtures", []):
            link_path = base_dir / link
            (source_root / "convs" / link_path.name).write_text(
                link_path.read_text(encoding="utf-8"), encoding="utf-8"
            )

        measured = runner_module.measure_record(
            binary=binary,
            source_root=source_root,
            record_id=record_id,
            workdir=workdir / reference / "run",
        )
        source_installations.append(measured["source_installation"])
        anomalies += [{**anomaly, "record": reference} for anomaly in measured["anomalies"]]

        for case in measured["cases"]:
            cells.append(
                _cell_for_case(
                    reference=reference,
                    gold_facts=entry.get("gold_facts", []),
                    record_text=record_text,
                    case=case,
                    receivers=receivers,
                    task=entry.get("continuation_task", ""),
                )
            )

    probe = corpus.get("contamination_probe")
    contamination = None
    if probe:
        contamination = runner_module.measure_neighbor_contamination(
            binary=binary,
            healthy_record=base_dir / probe["healthy_fixture"],
            broken_record=base_dir / probe["broken_fixture"],
            healthy_id=probe["healthy_id"],
            workdir=workdir / "contamination",
        )
        if contamination.get("anomaly"):
            anomalies.append(contamination["anomaly"])

    return report_module.build_report(
        corpus_version=str(corpus.get("corpus_version", "unknown")),
        cells=cells,
        anomalies=anomalies,
        harness_notes=(
            "receiver cells are unevaluated unless a provider credential is configured; "
            "pack-side measurements run offline"
        ),
    ) | {
        "source_installations": source_installations,
        "contamination_probe": contamination,
    }


def _cell_for_case(
    *,
    reference: str,
    gold_facts: list[dict],
    record_text: str,
    case: dict,
    receivers: list,
    task: str,
) -> dict:
    pack_text = case["stdout"] if case["exit_code"] == 0 else None
    answer = None
    receiver_results = []
    for entry in receivers:
        result = entry.run(pack_text=pack_text or "", task=task)
        receiver_results.append(result)
        if result["status"] == "evaluated" and answer is None:
            answer = result["answer"]

    scored = scoring.score_case(
        gold_facts=gold_facts,
        record_text=record_text,
        pack_text=pack_text,
        answer_text=answer,
        canaries=["IGNORE-THIS-INSTRUCTION-CANARY"],
        cell=f"{reference}/{case['budget_label']}",
    )

    built_ok = case["exit_code"] == 0
    refusal_expected = case["budget_label"] == "minimum-minus-one"
    if refusal_expected:
        robust = (not built_ok) and "budget is too small" in (case["stderr"] + case["stdout"])
    else:
        robust = built_ok
    source_pointer_present = (
        any(marker in pack_text for marker in ("show ", "\"show\""))
        if pack_text is not None
        else None
    )

    critical = [fact for fact in gold_facts if fact.get("critical", True)]
    if pack_text is None or not critical:
        presence = None
        omission_reported = None
    else:
        present = [fact for fact in critical if scoring.contains(pack_text, fact["value"])]
        presence = len(present) / len(critical)
        dropped = len(critical) - len(present)
        omission_reported = (case["truncated"] == "yes") if dropped else True

    pack_losses = scoring.attribute_pack_side(gold_facts, record_text, pack_text)

    return {
        "cell": scored["cell"],
        "pack_loss_counts": pack_losses,
        "record": reference,
        "budget": case["budget_label"],
        "budget_tokens": case["budget_tokens"],
        "exit_code": case["exit_code"],
        "pack_bytes": case["pack_bytes"],
        "computed_tokens": case["computed_tokens"],
        "relay_normalized_tokens": case["relay_normalized_tokens"],
        "deviation_tokens": case["deviation_tokens"],
        "truncated": case["truncated"],
        "latency_ms": round(case["latency_ms"], 3),
        "derived_writes": case["derived_writes"],
        "critical_recovery": scored["critical_recovery"],
        "continuation_completed": (
            None if answer is None else scored["critical_recovery"] == 1.0
        ),
        "provenance_clean": None if answer is None else not scored["unsupported_claims"],
        "source_pointer_present": source_pointer_present,
        "robust": robust,
        "pack_presence": presence,
        "omission_reported": omission_reported,
        "safe": scored["safe"] if answer is not None else None,
        "loss_counts": scored["loss_counts"],
        "unsupported_claims": scored["unsupported_claims"],
        "facts": scored["facts"],
        "receivers": receiver_results,
    }


def _unmeasurable_cell(reference: str, reason: str) -> dict:
    return {
        "cell": f"{reference}/unmeasurable",
        "record": reference,
        "budget": "unbudgeted",
        "critical_recovery": None,
        "pack_presence": None,
        "omission_reported": None,
        "safe": None,
        "continuation_completed": None,
        "provenance_clean": None,
        "source_pointer_present": None,
        "robust": False,
        "loss_counts": {name: 0 for name in scoring.LOSS_CLASSES},
        "reason": reason,
    }


def main(argv: list[str] | None = None) -> int:
    from . import corpus as corpus_module

    parser = argparse.ArgumentParser(description="run one Relay context fidelity baseline")
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--workdir", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="write the JSON report here")
    parser.add_argument("--receiver-config", type=Path)
    args = parser.parse_args(argv)

    corpus = corpus_module.load(args.corpus)
    problems = corpus_module.validate(corpus, args.corpus.parent)
    receivers = []
    if args.receiver_config:
        import json
        import os

        receivers = receiver_module.load_receivers(
            json.loads(args.receiver_config.read_text(encoding="utf-8")), env=dict(os.environ)
        )

    report = run_baseline(
        binary=args.binary,
        corpus=corpus,
        base_dir=args.corpus.parent,
        workdir=args.workdir,
        receivers=receivers,
    )
    report["corpus_problems"] = problems
    if args.out:
        report_module.write_report(report, args.out)
    print(report_module.render_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
