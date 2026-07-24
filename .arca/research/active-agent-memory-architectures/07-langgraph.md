# LangGraph

## Problem

LangGraph addresses state persistence and memory across multi-step execution graphs and multi-thread interactions. In long-running agentic workflows, execution graphs require deterministic state checkpoints to pause, resume, handle interrupts, and perform human-in-the-loop time travel. Beyond single-thread execution state, agents require persistent cross-thread state (long-term memory) to search, update, and recall user preferences, facts, and context across distinct conversations without cluttering thread-level state.

## Snapshot

- **Repository:** [`langchain-ai/langgraph`](https://github.com/langchain-ai/langgraph)
- **Stars:** 38,055 (as of 2026-07-24 snapshot)
- **Pinned commit:** [`31f90df3e6b0268fa77fd2d118a917d420b84a68`](https://github.com/langchain-ai/langgraph/commit/31f90df3e6b0268fa77fd2d118a917d420b84a68) (latest inspected `main` commit, dated 2026-07-21)
- **Latest release:** [`1.2.9`](https://github.com/langchain-ai/langgraph/releases/tag/1.2.9), published 2026-07-10

## Architecture

LangGraph separates short-term graph execution state (checkpoints) from long-term cross-thread state (stores). The monorepo separates core runtime packages, official checkpoint engines, and external infrastructure or cloud integrations.

### Core, checkpoint/store, SDK, and external packages

1. **Core (`libs/langgraph`):** Contains Pregel and `StateGraph` execution engines, state channels (`DeltaChannel`, `LastValue`, etc.), and high-level integrations. Core depends on `langgraph-checkpoint>=4.1.0,<5.0.0`.
2. **Checkpoint and store contracts/adapters (`libs/checkpoint`):** Owns `BaseCheckpointSaver`, `BaseStore`, in-memory implementations, and official checkpoint/store adapters. The observed independent package tag is `checkpoint==4.1.1`; checkpoint packages are versioned independently.
3. **Server/Cloud SDK (`libs/sdk`):** Provides Server/Cloud client SDKs; it is not a checkpoint/store package.
4. **External backend and cloud packages:** Separate service, infrastructure, and external adapter paths encapsulate physical storage while core Pregel owns execution semantics.

### Capture

Short-term execution state is captured automatically at each graph step. When compiled with a checkpointer, execution yields state updates indexed by `thread_id`. Each step writes state metadata, channel values, and pending writes via `put_writes()`. Long-term context is captured explicitly via the `BaseStore` interface (`put(namespace, key, value)`), where namespaces (e.g., `("user_id", "memories")`) isolate memory keys.

### Canonical and Derived Storage

- **Short-Term (Checkpoints):** Canonical storage maintains state checkpoints per `thread_id` alongside write logs (`put_writes`). `DeltaChannel` records channel updates alongside append operations.
- **Long-Term (`BaseStore`):** Canonical KV storage stores namespace-scoped key-value documents. Derived storage includes JSON path extraction and vector embeddings (`index` configurations) that populate search indices for semantic lookups (`search(namespace_prefix, query)`).

### Update and Delete

- **Checkpoints:** State channels support `'Overwrite'` or delta append modes. Reconstruction streams states from nearest full snapshot/value seed and replays writes. `delete_thread` removes thread checkpoints and write records. Crucially, deleting an ancestor write or DeltaSnapshot corrupts downstream reconstruction.
- **Store (`BaseStore`):** `put(namespace, key, value)` performs insert-or-update. `delete(namespace, key)` creates tombstones or deletes entries (`PutOp(..., None)`). Store deletion is represented as `PutOp(namespace, key, None)` at the base API. Semantic vector index maintenance, TTL, ranking, and persistence behavior are implementation-dependent; the inspected `InMemoryStore` updates its optional vectors but that is not a portable `BaseStore` guarantee.

### Retrieval

- **Thread Retrieval:** `get_tuple()` fetches state by `thread_id` and checkpoint ID, supporting time travel and thread replay.
- **Store Retrieval:** `get(namespace, key)` performs exact KV lookup. `search(namespace_prefix, query, filter, limit)` executes text or vector similarity search across indexed JSON fields within namespaces.

### Isolation and Recovery

- **Isolation:** Short-term state is isolated by `thread_id`. Long-term memory is isolated by hierarchical tuple namespaces (e.g., `(user_id, "settings")`). The framework does not perform automatic caller authorization; applications must pass authenticated namespaces.
- **Recovery:** In-memory stores (`InMemorySaver`, `InMemoryStore`) lose state on process restart. Persistent drivers (PostgreSQL, SQLite) recover state by loading full snapshots and replaying delta ancestors from durable disk storage.

## Release History

The monorepo tags core and sub-package releases independently. The public tag `v0.0.3` marks early observable releases; earlier release dates are unverified tag-only evidence.

| Release / Tag | Date | Scope & Milestone |
| :--- | :--- | :--- |
| `v0.0.3` | Early lineage | Observable early tag lineage (`0.1`/`0.2`/`0.3`/`0.4`/`0.5`/`0.6` rapid iterations). Tag-only evidence. |
| `1.1.0` | 2026-03-10 | Typed opt-in v2 `GraphOutput`/`StreamPart` behavior; the exact first-public date of `1.0.0` remains unestablished in the supplied evidence. |
| `1.2.6` | 2026-06-18 | Fixed nested subgraph parent `checkpoint_ns` inheritance regression and v3 stream abort cancellation. |
| `1.2.7` | 2026-06-30 | `DeltaChannel` overwrite-supersedes TS snapshot; JSON-roundtrip `'Overwrite'`; exit-mode task UUID fix. |
| `1.2.8` | 2026-07-06 | Fresh-thread `updateState` `DeltaChannel` fix (forces snapshot rather than stub checkpoint). |
| `1.2.9` | 2026-07-10 | `DeltaChannel` `updateState` metadata/counter fix. Current core release. |

*(Note: Independent package tags such as `checkpoint==4.1.1`, `checkpoint-postgres==3.1.0`, and `checkpoint-sqlite==3.1.0` demonstrate independent sub-package versioning.)*

## Issue-Tab Findings

Issue-tab sampling yielded 239 created and 485 updated issues since 2026-03-24. Open issue reports represent user claims and observations, not proven framework defects.

### Data Integrity & Loss (Core Engine)

| Issue | Status | Dates | Classification |
| :--- | :--- | :--- | :--- |
| [#8115](https://github.com/langchain-ai/langgraph/issues/8115) | Open | Opened 2026-06-17, Updated 2026-07-24 | User report / Claim |
| [#8217](https://github.com/langchain-ai/langgraph/issues/8217) | Open | Opened 2026-06-29, Updated 2026-07-24 | User report / Claim |

- **#8115:** Reports an alleged Pregel `loop.put_writes()` race and silent checkpoint loss; PR #8114 was not verified merged.
- **#8217:** Reports `GraphInterrupt` corruption conversion to a tool error in an async wrapper.

### Observability & API Ergonomics (SDK & Drivers)

| Issue | Status | Dates | Classification |
| :--- | :--- | :--- | :--- |
| [#8429](https://github.com/langchain-ai/langgraph/issues/8429) | Open | Opened 2026-07-24 | User report / Claim |
| [#7417](https://github.com/langchain-ai/langgraph/issues/7417) | Open | Opened 2026-04-05; open at snapshot; updated date not established in supplied evidence | User report / Cloud interaction |
| [#3716](https://github.com/langchain-ai/langgraph/issues/3716) | Open | Opened 2025-03-06, Updated 2026-07-23 | User report / Infrastructure |

- **#8429:** Reports that `close()` does not unblock active iterators.
- **#7417:** Reports Cloud re-execution after long tool calls; this is provider territory, not local-core proof.
- **#3716:** Reports `psycopg` HELLO SSL failure; assignments/comments suggest retry tuning but do not confirm the cause.

### Fixed Issues & Architectural Roadmaps

| Issue | Status | Dates | Classification |
| :--- | :--- | :--- | :--- |
| [#4973](https://github.com/langchain-ai/langgraph/issues/4973) | Open | Opened 2025-06-05, Updated 2026-07-23 | Maintainer feedback / Roadmap |
| [#8029](https://github.com/langchain-ai/langgraph/issues/8029) | Closed | Opened 2026-06-09, Closed 2026-06-17 | Fixed by linked release `1.2.6` |

- **#4973:** Maintainer-led discussion, not a defect report.
- **#8029:** GitHub status is Closed, not Fixed; fixed by linked release `1.2.6`.

The reports and the #8029 linked fix highlight these risks:

1. **Concurrency and state integrity:** #8115 reports an alleged `PregelLoop.put_writes()` race and silent checkpoint loss; linked PR #8114 was not verified merged.
2. **Interrupt and iterator dynamics:** #8217 reports `GraphInterrupt` conversion to a tool error in an async wrapper, and #8429 reports that `close()` does not unblock active iterators.
3. **Replay and external effects:** #7417 reports Cloud re-execution after long tool calls; this is provider territory, not local-core proof.
4. **Adapter transport resilience:** #3716 reports the SSL failure; assignment/comments suggest retry tuning but do not confirm the cause.

## Relay Lessons

1. **Separate Execution Checkpoints from Shared Memory:** Maintain explicit boundaries between per-thread execution graphs (checkpoints) and cross-thread namespace memory stores (`BaseStore`).
2. **Prune Safely:** Do not prune ancestor checkpoint writes blindly when using delta-based channels, as reconstruction depends on historical delta chains.
3. **Idempotent Step Execution:** Ensure tool invocations and external operations during graph steps are idempotent or tracked outside replayable state to prevent duplicate execution during time-travel or recovery.
4. **Enforce Namespace Tenant Authorization:** Application layers must validate tenant/user authorization on namespace prefixes before invoking store search or KV methods.

## Sources

- Monorepo source code at [`31f90df3e6b0268fa77fd2d118a917d420b84a68`](https://github.com/langchain-ai/langgraph/commit/31f90df3e6b0268fa77fd2d118a917d420b84a68).
- [Checkpoint Base Saver](https://github.com/langchain-ai/langgraph/blob/31f90df3e6b0268fa77fd2d118a917d420b84a68/libs/checkpoint/langgraph/checkpoint/base/__init__.py)
- [Store Base Class](https://github.com/langchain-ai/langgraph/blob/31f90df3e6b0268fa77fd2d118a917d420b84a68/libs/checkpoint/langgraph/store/base/__init__.py)
- [In-Memory Store Implementation](https://github.com/langchain-ai/langgraph/blob/31f90df3e6b0268fa77fd2d118a917d420b84a68/libs/checkpoint/langgraph/store/memory/__init__.py)
- GitHub Releases & Tags REST API (`langchain-ai/langgraph`)
- GitHub Issues REST API (`langchain-ai/langgraph`)
