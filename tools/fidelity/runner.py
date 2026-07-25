"""Disposable-root measurement runner for the Relay context-fidelity harness.

Every measured command runs against a throwaway root copied from the evaluated
records, so the source installation is never the target. Derived state that the
production read path publishes inside the disposable root is recorded as observed
behavior rather than hidden, because that behavior is itself evidence.
"""
from __future__ import annotations

import hashlib
import math
import re
import shutil
import subprocess
import time
from pathlib import Path

BUDGET_LABELS = (
    "unbudgeted",
    "generous",
    "mid",
    "minimum-plus-one",
    "minimum-minus-one",
)

_MINIMUM_PATTERN = re.compile(r"minimum required estimate is (\d+) tokens")


def snapshot(root: Path) -> dict[str, str]:
    """Map every file under `root` to a size and content digest."""
    root = Path(root)
    entries: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        entries[str(path.relative_to(root)).replace("\\", "/")] = f"{len(data)}:{digest}"
    return entries


def diff_snapshots(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    """Report what appeared, disappeared, or changed between two snapshots."""
    return {
        "added": sorted(set(after) - set(before)),
        "removed": sorted(set(before) - set(after)),
        "changed": sorted(key for key in set(before) & set(after) if before[key] != after[key]),
    }


def build_disposable_root(source_root: Path, destination: Path) -> Path:
    """Copy the archive records of `source_root` into a throwaway root."""
    source_root = Path(source_root)
    destination = Path(destination)
    (destination / "convs").mkdir(parents=True, exist_ok=True)
    source_convs = source_root / "convs"
    for record in sorted(source_convs.rglob("*.md")):
        target = destination / "convs" / record.relative_to(source_convs)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(record, target)
    return destination


def relay_normalized_tokens(pack: str, root: Path) -> int:
    """Replicate Relay's own estimate: normalize the root path, then ceil(len / 4).

    Mirrors `context_estimated_tokens` in src/main.rs, which measures text that is
    not what the receiver is sent. Keeping both figures side by side is the point.
    """
    escaped = str(Path(root)).replace("\\", "\\\\")
    normalized = pack.replace(escaped, "<relay-root>").replace(str(Path(root)), "<relay-root>")
    return math.ceil(len(normalized) / 4) if normalized else 0


def run_context(
    binary: Path, root: Path, record_id: str, budget_tokens: int | None = None
) -> dict:
    """Invoke the installed context path once and record its observable result."""
    args = [str(binary), "--relay-root", str(root), "context", record_id]
    if budget_tokens is not None:
        args += ["--budget-tokens", str(budget_tokens)]
    started = time.perf_counter()
    proc = subprocess.run(args, capture_output=True, text=True, timeout=120)
    latency_ms = (time.perf_counter() - started) * 1000
    pack = proc.stdout if proc.returncode == 0 else ""
    truncated = "unknown"
    for line in reversed(pack.splitlines()):
        if line.startswith("truncated:"):
            truncated = line.split(":", 1)[1].strip()
            break
    pack_bytes = len(pack.encode("utf-8"))
    computed = math.ceil(pack_bytes / 4) if pack else 0
    relay_style = relay_normalized_tokens(pack, root)
    return {
        "argv": args,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "pack_bytes": pack_bytes,
        "computed_tokens": computed,
        "relay_normalized_tokens": relay_style,
        "deviation_tokens": computed - relay_style,
        "truncated": truncated,
        "latency_ms": latency_ms,
    }


def discover_minimum_tokens(binary: Path, root: Path, record_id: str) -> int | None:
    """Ask the production path for the smallest budget it says it will accept."""
    probe = run_context(binary, root, record_id, budget_tokens=1)
    match = _MINIMUM_PATTERN.search(probe["stderr"] + probe["stdout"])
    return int(match.group(1)) if match else None


def budget_plan(accepted_minimum: int, unbudgeted_tokens: int) -> dict[str, int | None]:
    """Derive the five budget cases from the budget the tool actually accepts.

    The reported minimum is not used here: it was measured to understate what the
    budget check enforces, so planning from it would leave the tight cases untested.
    """
    ceiling = max(unbudgeted_tokens, accepted_minimum)
    return {
        "unbudgeted": None,
        "generous": ceiling * 2,
        "mid": max(accepted_minimum + 1, (accepted_minimum + ceiling) // 2),
        "minimum-plus-one": accepted_minimum + 1,
        "minimum-minus-one": max(accepted_minimum - 1, 1),
    }


def measure_record(
    *, binary: Path, source_root: Path, record_id: str, workdir: Path
) -> dict:
    """Measure one record across every budget case on a disposable root."""
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    disposable = build_disposable_root(source_root, workdir / "disposable-root")

    source_before = snapshot(source_root)
    records_before = _record_snapshot(disposable)
    status_before = _statuses(disposable)

    # The very first command sees a cold root, so its derived writes are the
    # honest answer to "does asking for a pack publish state?".
    cold_before = snapshot(disposable)
    unbudgeted = run_context(binary, disposable, record_id)
    cold_writes = _non_record_writes(diff_snapshots(cold_before, snapshot(disposable)))

    reported_minimum = discover_minimum_tokens(binary, disposable, record_id)
    accepted_minimum, rejections = _find_accepted_minimum(
        binary, disposable, record_id, reported_minimum
    )
    plan = budget_plan(
        accepted_minimum or reported_minimum or 1, unbudgeted["computed_tokens"]
    )

    cases = []
    for label in BUDGET_LABELS:
        before = snapshot(disposable)
        result = run_context(binary, disposable, record_id, budget_tokens=plan[label])
        derived = diff_snapshots(before, snapshot(disposable))
        result.update(
            {
                "budget_label": label,
                "budget_tokens": plan[label],
                "derived_writes": _non_record_writes(derived),
                "record_writes": [
                    path
                    for path in derived["added"] + derived["changed"]
                    if path.startswith("convs/")
                ],
            }
        )
        cases.append(result)

    anomalies = []
    if (
        reported_minimum is not None
        and accepted_minimum is not None
        and accepted_minimum > reported_minimum
    ):
        anomalies.append(
            {
                "kind": "reported-minimum-understates-accepted-budget",
                "record": record_id,
                "reported_minimum": reported_minimum,
                "smallest_accepted_budget": accepted_minimum,
                "rejected_budgets": rejections,
                "note": (
                    "the reported minimum is computed on root-normalized text while the "
                    "budget check measures the emitted pack"
                ),
            }
        )
    if cold_writes:
        anomalies.append(
            {
                "kind": "read-publishes-derived-state",
                "record": record_id,
                "paths": cold_writes,
                "note": "requesting a pack on a cold root wrote derived state",
            }
        )

    return {
        "record_id": record_id,
        "binary": str(binary),
        "disposable_root": str(disposable),
        "minimum_tokens": reported_minimum,
        "smallest_accepted_budget": accepted_minimum,
        "cold_read_derived_writes": cold_writes,
        "unbudgeted": unbudgeted,
        "cases": cases,
        "anomalies": anomalies,
        "source_installation": diff_snapshots(source_before, snapshot(source_root)),
        "records": diff_snapshots(records_before, _record_snapshot(disposable)),
        "status_before": status_before,
        "status_after": _statuses(disposable),
    }


def measure_neighbor_contamination(
    *, binary: Path, healthy_record: Path, broken_record: Path, healthy_id: str, workdir: Path
) -> dict:
    """Ask whether one unreadable record blocks a healthy record in the same root."""
    workdir = Path(workdir)
    alone_root = workdir / "healthy-alone" 
    (alone_root / "convs").mkdir(parents=True, exist_ok=True)
    shutil.copy2(healthy_record, alone_root / "convs" / Path(healthy_record).name)
    alone = run_context(binary, alone_root, healthy_id)

    shared_root = workdir / "healthy-with-broken"
    (shared_root / "convs").mkdir(parents=True, exist_ok=True)
    shutil.copy2(healthy_record, shared_root / "convs" / Path(healthy_record).name)
    shutil.copy2(broken_record, shared_root / "convs" / Path(broken_record).name)
    shared = run_context(binary, shared_root, healthy_id)

    blocked = alone["exit_code"] == 0 and shared["exit_code"] != 0
    result = {
        "healthy_id": healthy_id,
        "alone_exit_code": alone["exit_code"],
        "with_broken_neighbor_exit_code": shared["exit_code"],
        "message": shared["stderr"].strip(),
        "blocked": blocked,
        "names_the_broken_record": Path(broken_record).stem in shared["stderr"],
    }
    if blocked:
        result["anomaly"] = {
            "kind": "broken-neighbor-blocks-healthy-record",
            "record": healthy_id,
            "message": shared["stderr"].strip(),
            "names_the_broken_record": result["names_the_broken_record"],
            "note": (
                "a single unreadable record in the archive stopped a healthy record from "
                "producing any pack"
            ),
        }
    return result


def _find_accepted_minimum(
    binary: Path, root: Path, record_id: str, reported: int | None, attempts: int = 24
) -> tuple[int | None, list[int]]:
    """Find the smallest budget the CLI actually accepts, starting at the reported one."""
    if reported is None:
        return None, []
    rejected: list[int] = []
    budget = max(reported, 1)
    high: int | None = None
    low = 0
    for _ in range(attempts):
        if run_context(binary, root, record_id, budget_tokens=budget)["exit_code"] == 0:
            high = budget
            break
        rejected.append(budget)
        low = budget
        budget *= 2
    if high is None:
        return None, rejected
    while low + 1 < high:
        middle = (low + high) // 2
        if run_context(binary, root, record_id, budget_tokens=middle)["exit_code"] == 0:
            high = middle
        else:
            rejected.append(middle)
            low = middle
    return high, sorted(set(rejected))


def _non_record_writes(derived: dict[str, list[str]]) -> list[str]:
    return [
        path
        for path in derived["added"] + derived["changed"]
        if not path.startswith("convs/")
    ]


def _record_snapshot(root: Path) -> dict[str, str]:
    return {
        key: value
        for key, value in snapshot(root).items()
        if key.startswith("convs/")
    }


def _statuses(root: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for record in sorted((Path(root) / "convs").rglob("*.md")):
        text = record.read_text(encoding="utf-8", errors="replace")
        match = re.search(r'^status\s*=\s*"([^"]+)"', text, re.M)
        statuses[record.name] = match.group(1) if match else "unknown"
    return statuses
