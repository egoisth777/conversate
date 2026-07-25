# Relay goal design

Relay keeps Markdown records as source of truth and treats indexes as replaceable derived state. The implementation follows the preserved detailed authorities rather than introducing a second design here. This goal adds hook-counter outcome mechanics and a measurement harness that observes the shipped context path without changing it.

## Conformance map

| Concern | Detailed authority |
| :--- | :--- |
| Runtime root, scan engine, cache generations, fidelity | [Architecture](../space/relay-sp/what/architecture.md) |
| Source/derived/coordination ownership and compatibility fields | [Artifact manifest](../space/relay-sp/what/manifest.md) |
| Warm reads, search tiers, mutation journal, resume/context, repair | [Operational flows](../space/relay-sp/what/flows.md) |

The Rust CLI owns all archive mutations and recovery. Readers use one fresh snapshot. Writers hold the shared lock, publish a complete transaction journal before record replacement, publish derived cache artifacts in order, and make the manifest the final commit point. Compatibility aliases are accepted only where the manifest specifies them; new output uses canonical names.

## Target mechanics

### Hook counter outcomes (REQ-009, REQ-010, REQ-011)

`CounterStore::increment` currently returns `Option<u64>`, so lock exhaustion, overflow, and write failure collapse into the same empty answer that also means "no reminder", and a missing or malformed counter file falls back to zero. The target replaces that single answer with an explicit outcome value carrying committed count, rejected input, pre-replacement failure, or post-replacement durability uncertainty, and reports an unreadable or unparseable counter instead of resetting it. Contention is resolved by waiting for the session lock under a bounded, observable policy rather than a fixed 32-attempt loop, so a valid invocation is never lost to a scheduler accident. The hook caller maps outcomes to its exit contract and emits the tenth-turn reminder only for committed counts.

### Fidelity harness (REQ-012, REQ-013)

The harness is repository tooling, not shipped runtime behavior. It builds a disposable Relay root from the evaluated record and its link closure, invokes the installed `relay context` binary against that root, snapshots both roots before and after, scores gold facts deterministically, and writes a versioned redacted report. Provider receivers sit behind a configured adapter so ordinary local runs need no credentials or network access; an unavailable receiver is an explicitly unevaluated case, never a pass. The harness never writes to the source installation and never becomes a second source of truth for record content.
