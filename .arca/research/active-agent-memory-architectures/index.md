# Active agent-memory architectures

## Problem

Relay needs evidence from memory systems that are widely adopted and still changing now. Architecture documentation alone is not enough: repository issues show where persistence, extraction, retrieval, isolation, migration, and cost fail in practice.

## Scope

Snapshot date: 2026-07-24.

A project qualifies when:

1. its canonical public repository makes agent memory a core or separately inspectable subsystem;
2. it has a commit or release on or after 2026-03-24;
3. it has meaningful public adoption;
4. its Issues and Releases surfaces provide primary evidence.

GitHub stars and issue counts are volatile snapshots, not quality scores. Repository issue reports are user claims until code, maintainer response, or a fix confirms them. Pull requests are excluded from issue-only counts and themes.

## Selected architectures

| File | Project | Architecture class |
| :--- | :--- | :--- |
| `01-mem0.md` | Mem0 | LLM-extracted facts with vector storage, entity-vector association index, history, and temporal metadata |
| `02-letta.md` | Letta | Agent-edited in-context blocks plus archival memory |
| `03-graphiti.md` | Graphiti | Temporal and bi-temporal knowledge graph |
| `04-cognee.md` | Cognee | Persistent graph/vector ingestion and retrieval pipeline |
| `05-supermemory.md` | Supermemory | API-first memory and context engine |
| `06-memos.md` | MemOS | Self-evolving hybrid memory operating system with skill reuse |
| `07-langgraph.md` | LangGraph | Versioned graph checkpoints plus cross-thread memory stores |

The set balances adoption with distinct designs instead of choosing seven similar vector-retrieval products.

## Research method

Each project note records:

- canonical repository and pinned revision;
- popularity and recent activity snapshot;
- capture, storage, update, retrieval, forgetting, and prompt reconstruction path;
- public release history from first verifiable release/tag through the latest release;
- high-signal open and recently fixed issues, grouped by root problem;
- direct evidence versus researcher inference;
- lessons for Relay.

## Results

| File | Purpose |
| :--- | :--- |
| `00-selection.md` | Candidate screen and selection rationale |
| `release-timeline.md` | Cross-project chronological release history |
| `issue-patterns.md` | Recurring issue themes across repositories |
| `relay-implications.md` | Small, evidence-backed implications for Relay |
| `next-steps.md` | Prioritized, advisory follow-up actions derived from Relay implications |

Research is advisory and does not change Relay product authority.
