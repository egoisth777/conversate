# Relay goal test list

This checklist points to the executable Rust and Python suites, to the preserved product authorities, and to the checks added for the folded requirements. Every check below must be executable before its requirement can be implemented.

## Contract checks

| Check | Observable contract | Evidence source |
| :--- | :--- | :--- |
| T-ARCH | Runtime root and archive discovery never use the checkout or cwd; scan and cache behavior follows the architecture contract. | [Architecture](../space/relay-sp/what/architecture.md) and Rust tests |
| T-MAN | Source, derived, coordination, journal, and compatibility ownership match the manifest. | [Manifest](../space/relay-sp/what/manifest.md) and Rust tests |
| T-FLOW | Warm read, search-tier selection, mutation recovery, context trimming, and full repair follow the documented order. | [Flows](../space/relay-sp/what/flows.md) and Rust/Python tests |
| T-COMPAT | Canonical `relay_archive` output remains paired with deprecated `conversation_database`; glossary input alias remains accepted but is never emitted. | Manifest and integration tests |
| T-VERIFY | The repository suites remain runnable without changing runtime product code. | `cargo test`; `python -m pytest` |
| T-HOOK-LOSSLESS | A generated set of concurrent accepted submissions produces one durable increment per submission that is not reported as an explicit failure, with the expected total derived from the generated set rather than a fixed worker count. | [REQ-009](spec.md#req-009--lossless-session-turn-counting); Rust tests |
| T-HOOK-REMINDER | Across initial counts and submission ranges spanning several tenth-turn boundaries, each committed count divisible by ten emits exactly one reminder and no other committed count emits one. | [REQ-009](spec.md#req-009--lossless-session-turn-counting); Rust tests |
| T-HOOK-OUTCOMES | Injected lock, read, parse, overflow, replacement, and durability-sync faults each produce their classified outcome; pre-replacement failure preserves the published counter, malformed content is reported instead of reset, and post-replacement failure reports uncertainty. | [REQ-010](spec.md#req-010--explicit-hook-counter-outcomes); Rust tests |
| T-HOOK-PLATFORM | Counting, reminder, and isolation behavior hold on supported Unix and Windows semantics for sessions with distinct production storage identities, through the installed production hook path and without test-only behavioral paths. | [REQ-011](spec.md#req-011--deterministic-hook-behavior-on-supported-platforms); Rust tests |
| T-FIDELITY-CORPUS | The versioned corpus resolves at least five held-out real records plus every required synthetic boundary case, and commits no private record body or secret. | [REQ-012](spec.md#req-012--measured-context-fidelity-evidence); Python tests |
| T-FIDELITY-RUN | Every budget case runs against a disposable root, leaves the source installation byte-identical, records pack bytes, both token figures, provider telemetry, and loss attribution, and reports derived writes observed inside the disposable root. | [REQ-012](spec.md#req-012--measured-context-fidelity-evidence); Python tests |
| T-FIDELITY-GATE | The report states each decisive gate separately over the declared decision set, reports worst case, keeps efficiency descriptive, and changes no product output or schema. | [REQ-013](spec.md#req-013--fidelity-decision-gate); Python tests |

## Required commands

```text
cargo test
python -m pytest
```

Failures must be investigated and reported; they are not converted into passing evidence by changing unrelated product code.
