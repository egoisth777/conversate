# Relay goal specification

## Purpose

Relay is a short-lived Rust CLI and plugin workflow over a Markdown source of truth. It resolves a plugin installation root (normally `~/.relay/`), operates on the recursive Relay archive under `convs/`, and never uses the repository checkout or current working directory for runtime discovery or storage.

## Required behavior
Each `REQ-###` heading below is a stable, unique requirement identifier and Markdown anchor for goal, residual, ticket, and test references.

### REQ-001 — Archive authority

The Relay archive is authoritative human-readable handoff records. Derived indexes and caches may be rebuilt from it.
### REQ-002 — Public archive output

Public machine output uses `relay_archive` for the archive path. `conversation_database` remains an explicit deprecated compatibility alias with the same value.
### REQ-003 — Consistent archive snapshots

Archive-consuming commands take one symlink-safe snapshot and never serve a stale changed record.
### REQ-004 — Durable mutations

Mutations are serialized, journaled before replacement, recoverable after interruption, and publish derived artifacts only after ordered record writes; the manifest is published last.
### REQ-005 — Search tier selection

Search selects an installed `semble`, then opt-in `uvx semble` only when `RELAY_USE_UVX_SEMBLE=1`, otherwise body scoring fallback. Doctor reports the same selected tier.
### REQ-006 — Record schema

Records retain mandatory `summary`, `glossary`, and `qa` sections. Schema 2 adds environment, artifacts, checkpoint entries, and transcript weight without breaking legacy records.
### REQ-007 — Context reconstruction

`relay context` reconstructs required sections, adds bounded linked context, trims in the documented order, emits the v2 banner and final `truncated: yes|no`, and does not mutate status.
### REQ-008 — Read-only legacy import

Import reads legacy `~/.conversate/` as a read-only source, reports collisions, and never changes that source.
### REQ-009 — Lossless session turn counting

Every accepted `UserPromptSubmit` hook invocation with a non-empty session contributes exactly one durable increment to that session's counter under any level of concurrent contention, or ends in an explicit failure outcome defined by REQ-010. Recoverable lock contention is never a failure outcome, and no accepted invocation is silently dropped. For each committed count divisible by ten the hook emits the reminder exactly once, and no other committed count emits one.
### REQ-010 — Explicit hook counter outcomes

Each counter update reports a classified outcome: committed, rejected input, failure before replacement, or uncertain durability after replacement. A failure before replacement leaves the previously published counter intact and is distinguishable from rejected input. Unreadable or unparseable existing counter content is an explicit outcome, never a silent reset that republishes a lower value. A replacement whose durability synchronization fails is reported as uncertain and must be reconciled before retry. No terminal failure is returned as a successful no-op, and no temporary artifact is ever treated as the counter.
### REQ-011 — Deterministic hook behavior on supported platforms

Counting and reminder behavior is deterministic on supported Unix and Windows lock, rename, and durability semantics. Correctness must not depend on a fixed retry count, an added sleep, or a particular concurrency level, and counter state stays isolated between sessions that have distinct production storage identities. Behavior is exercised through the installed production hook path; fault injection is permitted only through seams that use that same path and persistence protocol, with no test-only behavioral divergence.
### REQ-012 — Measured context fidelity evidence

Relay retains a reproducible fidelity harness over the installed production `relay context` path. Each measured case runs against a disposable Relay root built from the evaluated records and their link closure, leaves the source installation unchanged, and reports any derived write the production path performs inside that disposable root. The versioned corpus covers at least five held-out real records plus synthetic boundary records for mixed transcript weights, oversized optional sections, closed linked branches, missing and malformed links, legacy schema, and injected instructions. Every case records pack bytes, an independently computed `ceil(pack bytes / 4)` value, Relay's reported root-normalized estimate, measured provider input tokens, latency, retries, and human intervention across unbudgeted, generous, mid, minimum-plus-one, and minimum-minus-one budgets, and attributes every missed gold fact to capture loss, trim loss, or an explicit unresolved cause. Reports are redacted and contain no private record body, credential, or raw receiver transcript.
### REQ-013 — Fidelity decision gate

The fidelity report states a separate pass or fail result for each decisive gate—critical recall, continuation, provenance, safety, truncation honesty, source recovery, and robustness—over a declared decision set, and reports the worst case rather than only the mean. Compression-efficiency numbers are descriptive because this baseline has no candidate change to compare. All decisive gates passing retains the harness as a regression gate and stops feature work; any decisive failure records the measured gap, and every remedy enters through a separate issue. Measuring fidelity authorizes no change to context output, record schema, trim order, linked digests, frontmatter, doctor, or save behavior.

## Folded issue map

| Issue requirement | Goal requirement |
| :--- | :--- |
| HOOK-INC-001, HOOK-INC-002 | [REQ-009](#req-009--lossless-session-turn-counting) |
| HOOK-INC-003, HOOK-INC-004 | [REQ-010](#req-010--explicit-hook-counter-outcomes) |
| HOOK-INC-005, HOOK-INC-006 | [REQ-011](#req-011--deterministic-hook-behavior-on-supported-platforms) |
| HFC-001 through HFC-006 | [REQ-012](#req-012--measured-context-fidelity-evidence) |
| HFC-007 | [REQ-013](#req-013--fidelity-decision-gate) |

Coverage obligations inside HOOK-INC-006 and HFC-002 are carried by the goal [test list](test-list.md); the requirements above carry the behavior.

## Authority links

The detailed, maintained contracts are preserved in:

- [Architecture](../space/relay-sp/what/architecture.md)
- [Artifact manifest](../space/relay-sp/what/manifest.md)
- [Operational flows](../space/relay-sp/what/flows.md)

This specification summarizes the delivered contract and adds the folded target requirements; those files remain the detailed product knowledge and are not duplicated here.
