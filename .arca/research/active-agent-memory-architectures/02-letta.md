# Letta (`letta-ai/letta`)

## Problem

Agent frameworks often handle long-term memory either by appending past messages to the context window until tokens run out or by using opaque automated fact-extraction background tasks. Letta addresses the challenge of stateful agent memory by making memory explicit, structured, and directly editable by the agent itself. Instead of relying purely on automatic context compression, Letta provides agents with explicit memory blocks (such as user personas or agent core state) and off-context archival memory for long-term semantic retrieval.

## Snapshot

- **Repository:** [`letta-ai/letta`](https://github.com/letta-ai/letta)
- **Stars / Date:** 23,943 stars (2,548 forks; 51 total open issue-tab items, of which 27 are issues excluding PRs) as of 2026-07-24
- **Pinned commit:** [`b76da9092518cbaa2d09042e52fdcbde69243e18`](https://github.com/letta-ai/letta/commit/b76da9092518cbaa2d09042e52fdcbde69243e18) (2026-07-03)
- **Latest published release:** [`0.16.8`](https://github.com/letta-ai/letta/releases/tag/0.16.8) (2026-05-14)

## Architecture

Letta divides agent memory into in-context core memory blocks, recall memory (conversation history), and archival memory (semantic passage storage).

### Capture

Memory updates in Letta are primary model actions rather than implicit background extractions. standard agents receive explicit core memory mutation tools (`core_memory_append`, `core_memory_replace`, `memory`, `memory_apply_patch`) to write directly into context blocks. For long-term storage, the agent uses `archival_memory_insert(content, tags)` to write text passages into off-context archival storage.

### Canonical vs. derived storage

The operational source of truth is relational state managed via SQLAlchemy (`Block`, `Agent`, `Passage`, `Archive`, `Message`).
- **Derived prompt views:** Prompt memory is a compiled view generated via `Memory.compile()`. It renders block values, system declarations, open file blocks, and dynamically attached tools into formatted system prompt blocks.
- **Git-enabled blocks (Opt-in):** For agents tagged with `GIT_MEMORY_ENABLED_TAG`, `GitEnabledBlockManager` treats Git / object storage (e.g., GCS) as the primary source of truth for full version history, using PostgreSQL as a read cache. Writes commit to Git first and sync to PostgreSQL, while reads pull from PostgreSQL for speed.

### Update and delete

- **Core memory blocks:** Updated or replaced via API or agent tools. Modifying a block forces prompt recompilation (`Memory.compile()`).
- **Archival passages & conversations:** Modified or deleted through their corresponding services; archive organization relationships use delete-orphan cascading.
- **Forgetting / Expiry:** There is no automated TTL or background fact-decay policy. Forgetting requires explicit block or passage deletion calls.
- **Summarization:** Summarization is optional and, in this inspected server version, initializes only when enabled and an OpenAI API key is available.
- **Embedding migrations:** Changing embedding models is currently not implemented in-place (`NotImplementedError` in agent state migration code). Updating embedding models requires manual re-indexing or export/import.

### Retrieval

- **Archival search:** Performed via `archival_memory_search(query, tags)`.
- **Backend divergence:** When integrated with Turbopuffer (`TPUF`), Letta uses hybrid vector + full-text search and returns rich rank metadata (vector rank, FTS rank, combined RRF score). When using the default SQL-based fallback, tag filtering is applied as a post-filter after query limits, and returned pass-through tuple relevance scores are static (`0.0`).

### Isolation and context management

- **Tenancy & isolation:** Passages, archives, and tags carry `organization_id` associations. Access checks enforce actor-scoped management (`actor: PydanticUser`). Archives can be shared across agents within the same organization.
- **Context window compaction:** Handled by a `Summarizer` service supporting `STATIC_MESSAGE_BUFFER` (retains a fixed recent suffix while summarizing older messages) and `PARTIAL_EVICT_MESSAGE_BUFFER` (evicts a fixed percentage of older messages). Summarization requires an explicit API configuration.

## Release history

Letta was formerly known as MemGPT. The table below lists chronological releases and tags from its earliest verifiable GitHub release to the snapshot date.

| Release / Tag | Date | Milestone / Highlights |
| :--- | :--- | :--- |
| [`0.1.6`](https://github.com/letta-ai/letta/releases/tag/0.1.6) | 2023-10-26 | Earliest verifiable GitHub Release. |
| [`0.3`](https://github.com/letta-ai/letta/releases/tag/0.3) | 2024-01-30 | Verifiable GitHub Release in the 0.3 line. |
| [`0.5.0`](https://github.com/letta-ai/letta/releases/tag/0.5.0) | 2024-10-15 | Verifiable GitHub Release in the 0.5 line. |
| [`0.6.0`](https://github.com/letta-ai/letta/releases/tag/0.6.0) | 2024-12-04 | Verifiable GitHub Release in the 0.6 line. |
| [`0.16.7`](https://github.com/letta-ai/letta/releases/tag/0.16.7) | 2026-03-31 | Verifiable GitHub Release in the 0.16 line. |
| [`0.16.8`](https://github.com/letta-ai/letta/releases/tag/0.16.8) | 2026-05-14 | **Latest Release.** Security fix: switched sandbox/server tool-result serialization from `pickle` to `JSON`. |

## Issue-tab findings

The repository issue tab contains user reports, maintainer discussions, and feature requests. Note that public issue reports represent user claims and are not proven defects unless backed by maintainer confirmation or linked fixes.

| Theme | Issue | Status | Opened / Updated-or-Closed | Evidence classification |
| :--- | :--- | :--- | :--- | :--- |
| **Context & Compaction** | [#3270](https://github.com/letta-ai/letta/issues/3270) (`sliding_window` compaction ignores percentage parameter) | Open | 2026-04-01 / 2026-07-18 | User report |
| **Context & Compaction** | [#3279](https://github.com/letta-ai/letta/issues/3279) (Summarizer capped by global context maximum) | Open | 2026-04-04 / 2026-07-24 | User report |
| **Context & Compaction** | [#3247](https://github.com/letta-ai/letta/issues/3247) (Provider context length defaulting to 30k) | Open | 2026-03-24 / 2026-07-24 | User report |
| **Data Integrity** | [#3399](https://github.com/letta-ai/letta/issues/3399) (Slash-labelled memory blocks unaddressable) | Open | 2026-07-07 / 2026-07-20 | Maintainer-engaged discussion |
| **Data Integrity / Security** | [#3388](https://github.com/letta-ai/letta/issues/3388) (Cross-session persistent core memory contamination report) | Open | 2026-06-19 / 2026-07-20 | User report / proposal |
| **Backend & Provider Protocol** | [#3384](https://github.com/letta-ai/letta/issues/3384) (vLLM missing `max_model_len` crashes discovery) | Open | 2026-06-16 / 2026-07-24 | Maintainer-engaged discussion |
| **Backend & Provider Protocol** | [#3386](https://github.com/letta-ai/letta/issues/3386) (Bedrock ignores encrypted credentials) | Open | 2026-06-16 / 2026-07-04 | User report |
| **Backend & Provider Protocol** | [#3382](https://github.com/letta-ai/letta/issues/3382) (LM Studio wrapper hides HTTP errors / mutates messages) | Closed | 2026-06-16 / Closed 2026-07-03 | Maintainer-closed |
| **Backend & Provider Protocol** | [#3381](https://github.com/letta-ai/letta/issues/3381) (Empty messages cause 500 server error) | Closed | 2026-06-16 / Closed 2026-07-03 | Maintainer-closed |
| **Performance & Execution** | [#3390](https://github.com/letta-ai/letta/issues/3390) (Missing Composio timeout leads to coroutine starvation) | Open | 2026-06-24 / 2026-07-14 | User report |
| **Governance & Security** | [#3410](https://github.com/letta-ai/letta/issues/3410) (Governance hooks for memory/tool PII and cost budgets) | Closed | 2026-07-24 / Closed 2026-07-24 | Maintainer-closed |

## What the issues reveal

1. **Context Compaction Boundaries:** User reports #3270 and #3279 highlight alleged compaction edge cases under varying model-window caps; neither behavior was reproduced or confirmed in the supplied evidence.
2. **Backend Portability Differences:** Retrieval behavior and provider integration (vLLM, Bedrock, Turbopuffer vs. SQL) vary in feature parity and error handling, making abstraction boundaries leak under non-standard LLM backends.
3. **Cache Synchronization Risks:** Dual-storage designs (like Git memory with PostgreSQL caching) require careful cache invalidation and prompt recompilation triggers whenever underlying blocks change out-of-band.

## Relay lessons

- **Separate Canonical Memory from Prompt Compilation:** Maintain a strict separation between persistent state records and the compiled prompt projection. Always track compilation freshness so direct data edits automatically recompile the prompt view.
- **Auditable Agent Self-Edits:** When agents are given memory mutation tools, treat writes as structured, tenant-scoped, bounded operations subject to schema validation rather than arbitrary prompt injection.
- **Explicit Retrieval Backend Contracts:** Ensure vector vs. relational search capabilities (scoring, rank metadata, and tag filtering logic) provide consistent contract guarantees regardless of the backend chosen.
- **Robust Compaction Accounting:** Provide clear context usage accounting and explicit summarization thresholds so context truncation failures fail predictably.

## Sources

- Inspecting repository commit [`b76da9092518cbaa2d09042e52fdcbde69243e18`](https://github.com/letta-ai/letta/commit/b76da9092518cbaa2d09042e52fdcbde69243e18) (2026-07-03).
- [`letta/schemas/block.py`](https://github.com/letta-ai/letta/blob/b76da9092518cbaa2d09042e52fdcbde69243e18/letta/schemas/block.py)
- [`letta/services/block_manager_git.py`](https://github.com/letta-ai/letta/blob/b76da9092518cbaa2d09042e52fdcbde69243e18/letta/services/block_manager_git.py)
- [`letta/services/agent_manager.py`](https://github.com/letta-ai/letta/blob/b76da9092518cbaa2d09042e52fdcbde69243e18/letta/services/agent_manager.py)
- [`letta/services/summarizer/summarizer.py`](https://github.com/letta-ai/letta/blob/b76da9092518cbaa2d09042e52fdcbde69243e18/letta/services/summarizer/summarizer.py)
- [GitHub Releases](https://github.com/letta-ai/letta/releases) and [GitHub Issues](https://github.com/letta-ai/letta/issues) APIs for `letta-ai/letta`
