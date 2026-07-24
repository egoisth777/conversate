# Cross-Project Issue Patterns in Active Agent-Memory Architectures

This document synthesizes recurring operational failure modes, design bottlenecks, and provider integration risks across seven active agent-memory architectures: **Mem0** (`01-mem0.md`), **Letta** (`02-letta.md`), **Graphiti** (`03-graphiti.md`), **Cognee** (`04-cognee.md`), **Supermemory** (`05-supermemory.md`), **MemOS** (`06-memos.md`), and **LangGraph** (`07-langgraph.md`).

Evidence snapshot date: **2026-07-24**.

---

## 1. Cross-Project Issue-Theme Matrix

The matrix below maps the ten core technical themes across all seven analyzed architectures. Support in repository issue tabs or release notes is classified as:
- **Primary Focus / Heavy Coverage ($\blacksquare$)**: Multiple high-signal issue reports or core architectural fixes in evidence.
- **Moderate Coverage ($\square$)**: Explicit issue reports or release notes present in repository evidence.
- **Minimal / Unmentioned (—)**: Theme not explicitly surfaced in repository issue sampling or architecture notes.

| Theme | Mem0 | Letta | Graphiti | Cognee | Supermemory | MemOS | LangGraph |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Data Integrity / Loss** | $\blacksquare$ | $\square$ | $\blacksquare$ | $\square$ | $\square$ | $\square$ | $\blacksquare$ |
| **Extraction Quality** | $\blacksquare$ | — | $\square$ | $\blacksquare$ | $\square$ | $\square$ | — |
| **Retrieval Relevance** | $\blacksquare$ | $\square$ | $\square$ | $\square$ | $\square$ | $\square$ | $\square$ |
| **Temporal Consistency** | — | — | $\blacksquare$ | — | — | — | $\square$ |
| **Isolation / Tenancy** | $\square$ | $\square$ | $\blacksquare$ | $\square$ | $\square$ | $\square$ | $\square$ |
| **Backend Portability** | $\blacksquare$ | $\blacksquare$ | $\blacksquare$ | $\blacksquare$ | $\square$ | $\square$ | $\square$ |
| **Migration / Schema** | — | $\square$ | $\square$ | $\blacksquare$ | $\blacksquare$ | $\square$ | — |
| **Performance / Cost** | — | $\square$ | $\square$ | $\square$ | $\square$ | $\blacksquare$ | — |
| **Observability / Recovery** | — | — | — | $\square$ | — | — | $\square$ |
| **API Ergonomics** | $\square$ | $\square$ | $\square$ | $\square$ | $\square$ | $\square$ | $\square$ |

---

## 2. Recurring Issue Patterns Across Architectures

### Pattern A: Backend Portability Leaks and Driver Discrepancies

#### Representative Issue Links
- **Mem0:** [#6562](https://github.com/mem0ai/mem0/issues/6562) (Open / User Report) — reports that TurboPuffer silently drops filter operators other than `gte`/`lte`. [#6560](https://github.com/mem0ai/mem0/issues/6560) (Open / User Report) — reports that UpstashVector `list()` ignores `top_k` and returns up to 100 items. [#6557](https://github.com/mem0ai/mem0/issues/6557) (Open / User Report) — reports incorrect TurboPuffer `euclidean_squared` search scores.
- **Letta:** [#3384](https://github.com/letta-ai/letta/issues/3384) (Open / Maintainer-engaged discussion) — reports vLLM discovery failing without `max_model_len`. [#3386](https://github.com/letta-ai/letta/issues/3386) (Open / User Report) — reports Bedrock ignoring encrypted credentials.
- **Graphiti:** [#1674](https://github.com/getzep/graphiti/issues/1674) (Open / User feature request) — AWS Bedrock embeddings and reranking RFC. [#1522](https://github.com/getzep/graphiti/issues/1522) (Closed / User report) — reports FalkorDB Cloud auth dropping URI username; closure alone is not a verified fix. [#1452](https://github.com/getzep/graphiti/issues/1452) (Closed / Fixed in release `v0.29.1`) — FalkorDB volume mounted at the wrong data path.
- **Cognee:** [#4187](https://github.com/topoteretes/cognee/issues/4187) (Open / User Report) — reports a Neo4j ID/property mismatch and dropped edge properties. [#4123](https://github.com/topoteretes/cognee/issues/4123) (Open / User Report) — reports Cypher/NL search importing the Postgres adapter without its extra.
- **MemOS:** [#1355](https://github.com/MemTensor/MemOS/issues/1355) (Closed / Fixed in `v2.0.22`) — Neo4j graph persistence errors under background write pipelines.

#### Shared Root Problem
Frameworks define abstract interfaces for vector search, graph querying, or LLM completion, but physical storage drivers and inference providers implement filtering, scoring metric math, payload constraints, and connection setups differently. When the abstract layer assumes SQL-like filtering or uniform vector similarity metrics across drivers, queries silently return degraded, unfiltered, or miscalculated result sets.

#### Architecture-Specific Exceptions
- **Letta** falls back from rich hybrid vector + full-text search (with RRF scoring) when using Turbopuffer to static `0.0` pass-through tuple scores under its SQL fallback adapter.
- **LangGraph** avoids cross-backend query semantics in core Pregel by delegating long-term memory retrieval to application-configured `BaseStore` implementations.

---

### Pattern B: Extraction non-determinism, validation failures, and model provider incompatibilities

#### Representative Issue Links
- **Mem0:** [#6571](https://github.com/mem0ai/mem0/issues/6571) (Open / User Report) — TS OSS Together Embeddings ignores `TOGETHER_API_BASE` while Together LLM honors it. [#6569](https://github.com/mem0ai/mem0/issues/6569) (Open / User Report) — TS OSS Gemini sends system prompts as `model` content role instead of `system`. [#6563](https://github.com/mem0ai/mem0/issues/6563) (Open / User Report) — reports malformed AWS Bedrock Converse requests for Amazon/Cohere tool calls; [#6556](https://github.com/mem0ai/mem0/issues/6556) (Open / User Report) — reports omitted tool-response `content` key.
- **Graphiti:** [#912](https://github.com/getzep/graphiti/issues/912) (Open / User Report) — Pydantic `ExtractedEntities` validation failure using Non-OpenAI / Ollama models.
- **Cognee:** [#4204](https://github.com/topoteretes/cognee/issues/4204) (Open / User Report) — Ontology extraction fails on `gpt-4o-mini` strict JSON schema. [#3870](https://github.com/topoteretes/cognee/issues/3870) (Open / Proposal) — Robust ingestion required for fixed-capacity local LLMs.
- **MemOS:** [#2148](https://github.com/MemTensor/MemOS/issues/2148) (Closed / Maintainer-assigned report) — `captureRunner` reportedly uses `reflectLlm` rather than the main LLM during batch reflection/model routing.

#### Shared Root Problem
Reports describe automated memory extraction pipelines as sensitive to structured JSON generation, tool calling, and schema compliance. Alternative or local providers may differ in role semantics or required output fields; the listed issues are not independent proof that every such configuration fails.

#### Architecture-Specific Exceptions
- **Letta** eliminates automatic extraction non-determinism in its core loop by making memory writes explicit, agent-driven model calls (`core_memory_append`, `archival_memory_insert`).
- **LangGraph** leaves fact extraction entirely to user-defined graph nodes rather than enforcing an automatic background ingestion pipeline.

---

### Pattern C: Multi-Store Synchronization and Data Loss Under Uncaught Pipeline Errors

#### Representative Issue Links
- **Mem0:** [#5245](https://github.com/mem0ai/mem0/issues/5245) (Open / User Report) — reports silent memory loss when batch embedding partially fails during v3 add pipeline execution. [#6411](https://github.com/mem0ai/mem0/issues/6411) (Closed / Fixed by PR #6412) — `Memory.reset()` claimed success while preserving vector data.
- **Graphiti:** [#1676](https://github.com/getzep/graphiti/issues/1676) (Open / User Report) — reports concurrent multi-group_id episode processing corrupting FalkorDB graphs. [#1659](https://github.com/getzep/graphiti/issues/1659) (Closed / Fixed by commit `3bb2d0b`) — `add_episode` re-binds the driver but single-group_id search did not.
- **Cognee:** [#4030](https://github.com/topoteretes/cognee/issues/4030) (Open / User Report) — reports stale session context asserting hard-deleted data. [#4029](https://github.com/topoteretes/cognee/issues/4029) (Closed / Triaged) — reports a byte-identical batch-add unique-ID race.
- **Supermemory:** [#1317](https://github.com/supermemoryai/supermemory/issues/1317) (Open / User Report) — reports failure to unlock local disk storage after server reboot. [#1203](https://github.com/supermemoryai/supermemory/issues/1203) (Closed / Fixed in `server-v0.0.7-rc.2`) — reports that documents >128KiB wedged the queue and prevented deletion.
- **LangGraph:** [#8115](https://github.com/langchain-ai/langgraph/issues/8115) (Open / User Report) — reports a Pregel `loop.put_writes()` race and silent checkpoint loss.

#### Shared Root Problem
Hybrid agent-memory architectures often maintain state across multiple physical backends (for example relational stores for raw messages, vector stores for embeddings, and graph stores for entities). The reports identify a risk that partial writes, re-indexing, or cleanup leave derived indexes out of sync; they do not prove that every such system lacks transactions or has data loss.

#### Architecture-Specific Exceptions
- **Graphiti** keeps episode and fact records in its graph model, but raw episode text is optional: `store_raw_episode_content=False` purges it. Derived embeddings and summaries are recomputable only when the required source evidence remains retained.
- **Letta**'s opt-in `GitEnabledBlockManager` treats Git object storage as the primary canonical source of truth and PostgreSQL as a read cache, so recovery for tagged agents should privilege Git.

---

### Pattern D: Isolation Leaks and Multitenancy Scope Enforcement

#### Representative Issue Links
- **Letta:** [#3388](https://github.com/letta-ai/letta/issues/3388) (Open / User Report) — Cross-session persistent core-memory contamination report.
- **Graphiti:** [#1676](https://github.com/getzep/graphiti/issues/1676) (Open / User Report) — Logical multi-tenancy `group_id` filters reportedly fail under FalkorDB graph concurrency.
- **Cognee:** [#4079](https://github.com/topoteretes/cognee/issues/4079) (Open / User Report) — Node-set-scoped hybrid search reportedly leaks other node sets.
- **Supermemory:** [#1246](https://github.com/supermemoryai/supermemory/issues/1246) (Closed / Maintainer-closed) — MCP list/graph endpoints reportedly returned records across projects while search remained container-scoped.

#### Shared Root Problem
The reports identify a risk that logical metadata tagging (such as `user_id`, `agent_id`, `organization_id`, or `group_id`) is inconsistently carried through SDKs, filters, or API routes. They do not prove a leak in every deployment.

#### Architecture-Specific Exceptions
- **Mem0** requires scope IDs inside `filters` for `search()` and `get_all()` in the current migration; `Memory.add()` still accepts top-level scope IDs. This is argument validation, not proof that every backend filter enforces authorization.
- **LangGraph** uses hierarchical tuple namespaces (for example `("tenant_id", "user_id", "memories")`) for scoping in `BaseStore`; namespaces are not authorization, so callers must derive and authorize them.

---

### Pattern E: Schema Migration, Embedding Invalidation, and System Upgrades

#### Representative Issue Links
- **Letta:** Note findings — Changing embedding models raises `NotImplementedError` in agent state migration code, requiring manual export/import or vector re-indexing.
- **Cognee:** [#3794](https://github.com/topoteretes/cognee/issues/3794) (Open / Feature request) — Schema-per-dataset pgvector isolation request.
- **Supermemory:** [#1325](https://github.com/supermemoryai/supermemory/issues/1325) (Open / User Report) — Migration failure on `server-v0.0.6` reporting schema collision (`observatory already exists`). [#1293](https://github.com/supermemoryai/supermemory/issues/1293) (Open / User report) — Upgrade from `v0.0.5` reportedly skipped the profile-buckets migration. [#1103](https://github.com/supermemoryai/supermemory/issues/1103) (Closed / Maintainer-closed) — Server upgrade reportedly resulted in zero vector search matches. [#1104](https://github.com/supermemoryai/supermemory/issues/1104) (Open / Maintainer-assigned user report) — Default English embedding model (`bge-base-en-v1.5`) reportedly degraded recall for non-English content.

#### Shared Root Problem
Embedding dimensions and graph schemas can make upgrades operationally sensitive. The reports and source notes support migration preflight and re-index planning; they do not establish that every upgrade breaks retrieval or crashes a database.

#### Architecture-Specific Exceptions
- **Cognee** invokes `recover_stale_cognify_runs_on_startup()` and has adapter-specific recovery paths; this does not prove that recovery repairs every pipeline.
- **MemOS** separates textual raw entries from vector state, but the supplied evidence does not establish automatic re-embedding as a general migration guarantee.

---

### Pattern F: Context Compaction Boundaries, Background Overhead, and Resource Starvation

#### Representative Issue Links
- **Letta:** [#3270](https://github.com/letta-ai/letta/issues/3270) (Open / User Report) — `sliding_window` compaction ignores percentage parameter. [#3279](https://github.com/letta-ai/letta/issues/3279) (Open / User Report) — Summarizer capped by global context maximum. [#3390](https://github.com/letta-ai/letta/issues/3390) (Open / User Report) — Missing tool call timeout leads to coroutine starvation.
- **Cognee:** [#3585](https://github.com/topoteretes/cognee/issues/3585) (Closed / User report; triage closed) — reports a Ladybug neighborhood assertion during multi-document ingestion. [#3516](https://github.com/topoteretes/cognee/issues/3516) (Open / Proposal) — requests fewer cognify LLM calls for resource-constrained backends.
- **MemOS:** [#2076](https://github.com/MemTensor/MemOS/issues/2076) (Closed / Fixed in `v2.0.23`) — user report of unpaginated plugin vector scans saturating CPU and consuming 4.2 GB RSS. [#1929](https://github.com/MemTensor/MemOS/issues/1929) (Closed / Fixed in `v2.0.22`) — fixed event-loop starvation when embedding engines hit 100% CPU utilization.

#### Shared Root Problem
Context management and background extraction can execute expensive compute operations. The reports identify main-thread execution, missing pagination, and absent timeouts as resource-starvation risks; they do not establish those outcomes for every deployment.

#### Architecture-Specific Exceptions
- **LangGraph** provides checkpoints and explicit application-controlled retention; its checkpoint/store APIs do not perform automatic compaction.
- **Supermemory** release `server-v0.0.7-rc.2` offloads workflow-step data past a local Rivet KV limit; this is not evidence of cloud-worker offloading.

---

## 3. What Issue Tabs Cannot Prove

While repository issue tabs surface primary evidence of real-world friction and operational edge cases, they have strict analytical limits:

1. **User Claims vs. Verified Bugs:** Issue reports represent user observations, configuration errors, environment mismatches, or unverified claims until confirmed by maintainer responses, reproduction scripts, or merged pull requests.
2. **Absence of Evidence is Not Evidence of Quality:** A low open issue count may reflect narrow adoption, restricted access, low community reporting activity, or recent repository cleanup rather than superior software quality or stability.
3. **Selective Reporting Bias:** Issues surface edge-case failures, provider breakage, and setup friction while remaining silent on stable, working production paths.
4. **Quantification Delusion:** Aggregate issue metrics or star counts do not measure architectural correctness, data safety guarantees, or benchmark retrieval quality.

---

## 4. Relay implications

This study makes no new storage, extraction, embedding, or migration recommendation for Relay. The corrected, advisory priorities are maintained in [Relay implications](relay-implications.md): defend Relay's existing archive-authority, single-writer, rebuildable-derived-state, bounded-retrieval, and truthful-outcome invariants with executable proof. In particular, this study does **not** recommend adding a relational store, LLM extraction pipeline, vector/embedding lifecycle, graph store, or owned embedding-migration machinery.
