"""Corpus definition and validation for the Relay context-fidelity harness.

The corpus names what will be measured; it never stores record content. Held-out
real records are referenced by redacted identifier so private handoff text stays in
the Relay archive, and synthetic boundary fixtures live beside this module.

Validation returns problems instead of raising, so an incomplete corpus can be
reported honestly rather than silently skipped.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

MINIMUM_HELD_OUT_RECORDS = 5
MINIMUM_RECEIVERS = 2

REQUIRED_BOUNDARIES = (
    "mixed-weights",
    "oversized-optional",
    "closed-links",
    "missing-link",
    "malformed-link",
    "legacy-schema",
    "injected-instructions",
)

REQUIRED_BUDGETS = (
    "unbudgeted",
    "generous",
    "mid",
    "minimum-plus-one",
    "minimum-minus-one",
)

GOLD_FACT_KINDS = (
    "path",
    "command",
    "id",
    "version",
    "constraint",
    "decision",
    "test-result",
    "pending-work",
)

_SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9]{16,}"),
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"\b(?:api[_-]?key|password|secret)\s*[:=]\s*\S{8,}", re.IGNORECASE),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
)


def load(path: Path | str) -> dict:
    """Read a corpus manifest."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate(corpus: dict, base_dir: Path | str) -> list[str]:
    """Return every reason this corpus is not yet a complete measurement input."""
    base = Path(base_dir)
    problems: list[str] = []

    if not str(corpus.get("corpus_version", "")).strip():
        problems.append("corpus_version is missing")

    held_out = corpus.get("held_out_records", [])
    if len(held_out) < MINIMUM_HELD_OUT_RECORDS:
        problems.append(
            f"held-out records: {len(held_out)} of {MINIMUM_HELD_OUT_RECORDS} required"
        )
    for record in held_out:
        reference = record.get("reference", "<unnamed>")
        if "body" in record or "content" in record:
            problems.append(f"{reference} carries an inline record body; reference it instead")
        problems.extend(_gold_fact_problems(record, reference))

    synthetic = corpus.get("synthetic_records", [])
    covered = {record.get("boundary") for record in synthetic}
    for boundary in REQUIRED_BOUNDARIES:
        if boundary not in covered:
            problems.append(f"synthetic boundary case is missing: {boundary}")
    for record in synthetic:
        reference = record.get("reference", "<unnamed>")
        problems.extend(_gold_fact_problems(record, reference))
        fixture = record.get("fixture")
        if not fixture:
            problems.append(f"{reference} declares no fixture file")
            continue
        fixture_path = base / fixture
        if not fixture_path.is_file():
            problems.append(f"fixture file is missing: {fixture}")
            continue
        fixture_text = fixture_path.read_text(encoding="utf-8", errors="replace")
        if _contains_secret(fixture_text):
            problems.append(f"fixture appears to contain a secret: {fixture}")
        for fact in record.get("gold_facts", []):
            value = str(fact.get("value", ""))
            if value and not _present(fixture_text, value):
                problems.append(
                    f"{reference} declares a gold fact that its fixture never states: {value}"
                )
        for link in record.get("link_fixtures", []):
            if not (base / link).is_file():
                problems.append(f"link fixture is missing: {link}")

    budgets = corpus.get("budgets", [])
    for budget in REQUIRED_BUDGETS:
        if budget not in budgets:
            problems.append(f"budget case is missing: {budget}")

    receivers = corpus.get("receivers", [])
    if len(receivers) < MINIMUM_RECEIVERS:
        problems.append(
            f"receiver targets: {len(receivers)} of {MINIMUM_RECEIVERS} required"
        )
    for receiver in receivers:
        for field in ("provider", "model", "host"):
            if not receiver.get(field):
                problems.append(f"receiver entry is missing {field}")

    return problems


def _present(text: str, value: str) -> bool:
    return " ".join(value.split()).casefold() in " ".join(text.split()).casefold()


def _gold_fact_problems(record: dict, reference: str) -> list[str]:
    facts = record.get("gold_facts", [])
    if not facts:
        return [f"{reference} declares no gold fact"]
    problems = []
    for fact in facts:
        if fact.get("kind") not in GOLD_FACT_KINDS:
            problems.append(f"{reference} has a gold fact of unknown kind: {fact.get('kind')}")
        if not str(fact.get("value", "")).strip():
            problems.append(f"{reference} has a gold fact with no value")
        if not str(fact.get("source", "")).strip():
            problems.append(f"{reference} has a gold fact with no source location")
    return problems


def _contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)
