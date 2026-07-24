# Relay implications

## Standing

This note is advisory research output under `.arca/research/active-agent-memory-architectures/`. It derives the smallest evidence-backed lessons for Relay from the seven project notes (`01-mem0.md` through `07-langgraph.md`) and their issue histories, snapshot date 2026-07-24. It does not modify delivered Relay authority; adopting any recommendation requires the normal issue-folding route (`.arca/index.md`, P1). Throughout, repository issue reports are user claims and observations, not proven defects, unless a note records a maintainer confirmation or a release-linked fix.

## Relay baseline

Relay already holds the position most of the seven systems are struggling toward: a single human-readable canonical store (the Markdown archive, [REQ-001](../../current/spec.md)), fully rebuildable derived artifacts (index-v2 cache, postings, `index.jsonl` per the [manifest](../../space/relay-sp/what/manifest.md)), one journaled, ordered, manifest-last mutation path with idempotent replay ([REQ-004](../../current/spec.md), [flows](../../space/relay-sp/what/flows.md)), tiered search with a deterministic fallback ([REQ-005](../../current/spec.md)), and a budget-aware, non-mutating context projection ([REQ-007](../../current/spec.md)). The implications below are therefore mostly about defending invariants Relay already has, not adding machinery.

## Lessons by concern

### 1. Canonical vs derived state

**Evidence.** The public designs distinguish source inputs from queryable or prompt-facing state in different ways. Mem0 keeps raw chat history in SQLite separate from extracted facts ([01](01-mem0.md)); Letta keeps relational state and compiles prompt memory as a derived view ([02](02-letta.md)); Graphiti retains episodic/entity records while derived embeddings and summaries are recomputable only when their needed source evidence remains preserved ([03](03-graphiti.md)); and Cognee separates a relational ledger from graph/vector indexes ([04](04-cognee.md)). Supermemory's public contract distinguishes document/conversation inputs from returned memories, profiles, and search results, while its hosted canonical schema is not public ([05](05-supermemory.md)). MemOS and LangGraph likewise distinguish capture/retrieval records from integration-layer prompt construction ([06](06-memos.md), [07](07-langgraph.md)).

**Lesson.** Relay's archive-authority rule (REQ-001) is the correct invariant; the risk is erosion, not absence. No future feature may write information that exists only in a derived artifact, and no option may discard archive content that derived state depends on (the Graphiti raw-purge foot-gun).

### 2. Idempotent ingest

**Evidence.** Partial-failure ingest is a recurring reported failure class: Mem0 [#5245](https://github.com/mem0ai/mem0/issues/5245) reports silent memory loss when batch embedding partially fails (user report); Graphiti [#290](https://github.com/getzep/graphiti/issues/290) reported rate limits leaving partial graph state without a clear recovery path (closed); Supermemory [#1302](https://github.com/supermemoryai/supermemory/issues/1302) reported that re-ingesting a failed document without modification could not trigger re-extraction (maintainer-closed), and [#1203](https://github.com/supermemoryai/supermemory/issues/1203) that >128KiB inputs wedged the queue until a release-linked fix (`server-v0.0.7-rc.2`). Cognee [#4029](https://github.com/topoteretes/cognee/issues/4029) reported a unique-ID race on byte-identical batch adds (triage closed).

**Lesson.** Relay's startup replay is already specified idempotent; the same property must hold for re-running legacy import (REQ-008) and for repeating any interrupted mutation: same input twice must converge to the same archive and derived state, with collisions reported identically, never duplicated or half-applied.

### 3. Atomic and reconcilable multi-store writes

**Evidence.** Mem0's note states vector and entity stores "operate independently without a unified distributed transaction," so partial failures can diverge state ([01](01-mem0.md)). Graphiti's note states multi-stage ingestion "lacks transactional rollback" across LLM calls, embeddings, and graph writes ([03](03-graphiti.md)). Cognee's note states operations across graph, vector, relational, and session caches "are not globally atomic" ([04](04-cognee.md)).

**Lesson.** Relay avoids this whole class by having one writer, one journal, and one commit point (manifest published last). The lesson is a guard: any proposal that adds a second independently-written store must either publish behind the existing single commit point or be provably reconcilable from the archive alone — otherwise it imports the largest reported failure class across these systems.

### 4. Deterministic deletion and replay

**Evidence.** Cognee [#4030](https://github.com/topoteretes/cognee/issues/4030) reports stale session context asserting hard-deleted data (user report, not proof of a universal defect). MemOS [#1966](https://github.com/MemTensor/MemOS/issues/1966) fixed infinite recursion caused by ghost trace memory nodes (fixed in `v2.0.22`). Graphiti's temporal soft-invalidation deliberately preserves superseded facts, and its note observes this does not satisfy hard deletion/governance needs ([#1679](https://github.com/getzep/graphiti/issues/1679), feature request). LangGraph's note warns that deleting an ancestor write or delta snapshot corrupts downstream reconstruction ([07](07-langgraph.md)).

**Lesson.** Deletion in Relay must be total across derived state — no ghost postings, cache rows, or reverse references after a record is removed or renamed — and pruning must respect ordering dependencies, which Relay's manifest rule already encodes (obsolete cache generations pruned only after a successful manifest commit). `regen-refs` and `rebuild-index --full` must converge to the same state as the incremental path.

### 5. Isolation

**Evidence.** Isolation enforced away from the data boundary leaks: Mem0 [#6562](https://github.com/mem0ai/mem0/issues/6562) reports a backend silently dropping filter operators (user report); Graphiti [#1676](https://github.com/getzep/graphiti/issues/1676) reports concurrent multi-`group_id` processing corrupting data across FalkorDB graphs (user report), while [#1659](https://github.com/getzep/graphiti/issues/1659) (search not re-binding the per-group driver) was fixed by a linked commit; Cognee [#4079](https://github.com/topoteretes/cognee/issues/4079) reports node-set-scoped search leaking other node sets (user report); Supermemory [#1246](https://github.com/supermemoryai/supermemory/issues/1246) reported MCP list/graph endpoints returning records across all projects while search stayed scoped (maintainer-closed).

**Lesson.** Relay is single-user, so its isolation analog is root and scope confinement: every command resolves the same installation root, never the checkout or working directory; `~/.conversate/` stays strictly read-only (REQ-008); and every archive-consuming surface — list, search, show, context, doctor — goes through the same single-snapshot resolution (REQ-003). The Supermemory case generalizes: a scope rule enforced on one endpoint but not all of them is a leak.

### 6. Exact-source recovery

**Evidence.** Supermemory [#1103](https://github.com/supermemoryai/supermemory/issues/1103) reported zero vector matches after a server upgrade (maintainer-closed); recovery from such states depends on raw records surviving independently of derived indexes, which its note lists as the first Relay lesson ([05](05-supermemory.md)). Cognee's adapters self-heal by discarding corrupted Ladybug WAL state and rebuilding LanceDB tables on schema drift ([04](04-cognee.md)). Letta's embedding migration is not implemented in-place (`NotImplementedError`), forcing manual re-index or export/import ([02](02-letta.md)).

**Lesson.** Relay's recovery story — `RELAY_NO_CACHE=1` as reference bypass, `rebuild-index --full` as complete reparse, `doctor --fix` — is exactly what these systems retrofit under pressure. Preserve the invariant that every derived byte is reproducible from the archive alone, and treat any drift between the cached path and the reference bypass as a defect, not a tuning matter.

### 7. Bounded retrieval

**Evidence.** MemOS [#2076](https://github.com/MemTensor/MemOS/issues/2076) — unpaginated full-table scans pinning CPU — was fixed in `v2.0.23`. Mem0 [#6560](https://github.com/mem0ai/mem0/issues/6560) reports a backend ignoring `top_k` (user report). Graphiti [#402](https://github.com/getzep/graphiti/issues/402) reports label propagation lacking an iteration cap (user report). Letta [#3270](https://github.com/letta-ai/letta/issues/3270)/[#3279](https://github.com/letta-ai/letta/issues/3279) report compaction parameters being ignored or capped unexpectedly (user reports).

**Lesson.** Relay's context pack is already budget-aware with a documented trim order and a `truncated: yes|no` marker (REQ-007); linked context is bounded to one hop. Keep every unbounded surface capped: the parallel body fallback scan, linked-digest expansion, and any future candidate set need explicit, documented limits — and parameters that claim to bound work must demonstrably do so (the Letta reports are about bounds that silently didn't bind).

### 8. Migrations

**Evidence.** Supermemory's upgrade sequence produced schema collisions ([#1325](https://github.com/supermemoryai/supermemory/issues/1325), user report), a skipped migration ([#1293](https://github.com/supermemoryai/supermemory/issues/1293), user report), and the zero-match upgrade above; it then added persisted embedding plans in `server-v0.0.5` to fail fast on mismatches. MemOS's note records that embedding-dimension changes break storage portability without migration scripts ([06](06-memos.md)). Mem0's `v2.0.0` migration moved top-level scope IDs into `filters` for `search()` and `get_all()`; `Memory.add()` still accepts them at top level ([01](01-mem0.md)).

**Lesson.** Relay's pattern — additive record schema (`relay_schema = 2`), generation-named cache with a manifest commit point, and deprecated aliases retired only via explicit deprecation plans — is the low-risk shape. Derived formats should never be migrated in place: a format change is a new generation, built from the archive, discarded on failure. Record-schema changes stay additive; breaking input changes get the Mem0 treatment only with an explicit plan.

### 9. Observability

**Evidence.** Silent success is the recurring reported symptom: Mem0 [#6411](https://github.com/mem0ai/mem0/issues/6411) — `reset()` claiming success while preserving memories — was fixed by PR #6412; MemOS [#1493](https://github.com/MemTensor/MemOS/issues/1493) — HTTP 200 without storing memory — was fixed in `v2.0.22`; Supermemory's note flags background capture swallowing errors and recommends explicit job status ([05](05-supermemory.md)); Cognee [#3553](https://github.com/topoteretes/cognee/issues/3553) proposes surfacing processing lag instead of silent empty recall, and [#3681](https://github.com/topoteretes/cognee/issues/3681) proposes a doctor/status facility Relay already has.

**Lesson.** Every Relay degradation must be visible in output: search tier actually selected (already required by REQ-005 and reported by doctor), truncation (already `truncated: yes|no`), journal recovery on startup, and cache rebuild/repair events. A command must never report success without the corresponding observable effect on the archive or derived state.

### 10. Test gates

**Evidence.** The issue histories show which gates would have caught what: interruption/partial-failure gates (Graphiti #290, Mem0 #5245, Supermemory #1203); no-op-success gates (Mem0 #6411, MemOS #1493); lifecycle-hook gates — MemOS [#2144](https://github.com/MemTensor/MemOS/issues/2144) reports `shouldArchiveIdle` defined but never invoked (open, needs triage, not a proven defect); backend-parity gates — Letta's SQL fallback returns static `0.0` relevance scores and post-filters tags after the query limit, unlike its Turbopuffer path ([02](02-letta.md)); migration preflight gates (Supermemory #1325/#1293).

**Lesson.** Relay's proof authority is `test-list.md`; the highest-value gates implied by this evidence are enumerated as recommendations below. The common thread: test the invariant (convergence, completeness, honesty of output), not the implementation step.

## Recommendations, ranked

Advisory only; each would enter through a new issue folded in P1. None modifies delivered authority here.

### Now — defend existing invariants with executable proof

| ID | Recommendation | Driving evidence |
| :--- | :--- | :--- |
| N-1 | Interruption matrix over the mutation order (journal publish → record replacement → cache → export → manifest → journal unlink): kill at each boundary, assert replay converges and is idempotent on double-replay. | Graphiti #290, Mem0 #5245, Supermemory #1203 |
| N-2 | Derived-equivalence gate: cached path, `RELAY_NO_CACHE=1`, and post-`rebuild-index --full` results agree; `index.jsonl` stays byte-stable and id-sorted. | Supermemory #1103; Cognee schema-drift self-healing |
| N-3 | Deletion-completeness gate: after record removal/rename, zero ghost postings, cache rows, or reverse refs; incremental result equals `regen-refs` + full rebuild result. | MemOS #1966, Cognee #4030 (user report) |
| N-4 | Truthful-outcome gate: every mutating command's success output is asserted against an observable state change (or an explicit no-op message). | Mem0 #6411, MemOS #1493 |

### Next — close small gaps

| ID | Recommendation | Driving evidence |
| :--- | :--- | :--- |
| X-1 | Doctor surfaces recovery events: report when startup replayed a journal and when derived state was rebuilt due to integrity or source drift, not just tier and fidelity. | Cognee #3553/#3681, Supermemory silent-capture lesson |
| X-2 | Document and test explicit caps on the body-fallback scan and linked-digest expansion; add a determinism regression for the context trim order, asserting the bound parameters actually bind. | MemOS #2076, Mem0 #6560, Letta #3270/#3279 |
| X-3 | Cache-format version preflight: an index-v2 generation carries its format version; an older binary refuses (and rebuilds) rather than misreads a newer generation. Format change = new generation from the archive, never in-place migration. | Supermemory #1325/#1293/#1103 |
| X-4 | Import idempotence gate: running legacy import twice yields an unchanged archive and an identical collision report. | Supermemory #1302, Cognee #4029 |

### Later — only if the trigger arrives

| ID | Recommendation | Trigger and evidence |
| :--- | :--- | :--- |
| L-1 | Retire `conversation_database` and `dict` aliases via the separate deprecation plans the manifest already requires — with a Mem0-style explicit breaking migration notice. | Only when a consumer inventory exists; Mem0 v2.0.0 filter migration |
| L-2 | External-tier contract test: pin the selection rule and output shape expected from an installed `semble`/`uvx semble` so upstream changes surface as a failed contract, not silent behavior drift. | Only if semble behavior drift is observed; Letta Turbopuffer-vs-SQL divergence |
| L-3 | If multi-writer access or any second store is ever proposed: require single-commit-point publication or a proven reconcile-from-archive path as an acceptance criterion before design work proceeds. | Only on such a proposal; Mem0/Graphiti/Cognee non-atomic multi-store evidence |

## Rejected machinery

The strongest cross-project finding is negative: most of the reported failure mass across the seven repositories comes from machinery Relay does not need.

- **No graph database layer.** Reported corruption and drift concentrate at graph-backend boundaries: Graphiti #1676/#1659 (group routing), Cognee [#4187](https://github.com/topoteretes/cognee/issues/4187) (Neo4j property mismatch, user report), MemOS #1355 (Neo4j persistence, fixed in `v2.0.22`). Relay's reverse references over Markdown, with `regen-refs` as full repair, already provide the linkage its context pack needs.
- **No vector store or owned embeddings.** Backend abstraction leaks (Mem0 #6562/#6560/[#6557](https://github.com/mem0ai/mem0/issues/6557)), embedding-model migration pain (Letta's `NotImplementedError`, MemOS dimension portability, Supermemory [#1104](https://github.com/supermemoryai/supermemory/issues/1104)/[#1336](https://github.com/supermemoryai/supermemory/issues/1336)/[#1320](https://github.com/supermemoryai/supermemory/issues/1320)), and upgrade-induced recall loss (#1103) are the cost of owning vector lifecycle. Relay's tier design already externalizes this: semantic search is delegated to an optional, external `semble`, with trigram postings and body scoring as deterministic fallbacks. Relay should never internalize an embedding store.
- **No LLM extraction pipeline.** Extraction is non-deterministic and quality-fragile across providers: Graphiti [#912](https://github.com/getzep/graphiti/issues/912) (schema validation failures on non-OpenAI models, user report), Cognee [#4204](https://github.com/topoteretes/cognee/issues/4204) (user report), and the Mem0 [#4573](https://github.com/mem0ai/mem0/issues/4573) user audit expressing relevance concerns over 10,134 entries (rates unverified). Relay records are human-authored handoffs; there is no derived-fact layer to extract, so this entire failure class is avoided by construction.
- **No image or multimodal storage.** None of the seven notes contains evidence that Relay's handoff-record use case needs binary or image ingestion; adding it would break the property that the entire archive is human-readable Markdown from which all derived state rebuilds.

## Sources

- Project notes in this study: [00-selection.md](00-selection.md), [01-mem0.md](01-mem0.md), [02-letta.md](02-letta.md), [03-graphiti.md](03-graphiti.md), [04-cognee.md](04-cognee.md), [05-supermemory.md](05-supermemory.md), [06-memos.md](06-memos.md), [07-langgraph.md](07-langgraph.md). All issue links above are drawn from those notes; issue reports remain user claims unless a note records a maintainer confirmation or release-linked fix.
- Delivered Relay authority, read-only for mapping: [specification](../../current/spec.md), [architecture](../../space/relay-sp/what/architecture.md), [artifact manifest](../../space/relay-sp/what/manifest.md), [flows](../../space/relay-sp/what/flows.md).
