# Active Agent-Memory Architectures: Cross-Project Release Timeline

This document establishes a cross-project chronological timeline for seven active agent-memory architectures evaluated as of the **2026-07-24** snapshot: **Mem0**, **Letta**, **Graphiti**, **Cognee**, **Supermemory**, **MemOS**, and **LangGraph**.

---

## 1. First Verifiable Release

The table below lists the earliest verifiable release or tag recorded for each project across public primary evidence (GitHub Releases, Git tags, or npm package registry entries).

| Project | First Verifiable Version / Tag | Date | Evidence Classification | Primary Source / Context |
| :--- | :--- | :--- | :--- | :--- |
| **Cognee** | `0.0.1` | 2023-10-08 | GitHub Release | Earliest verifiable public GitHub release tag for [`topoteretes/cognee`](https://github.com/topoteretes/cognee/releases/tag/0.0.1). |
| **Letta** (MemGPT) | `0.1.6` | 2023-10-26 | GitHub Release | Earliest verifiable GitHub Release for [`letta-ai/letta`](https://github.com/letta-ai/letta/releases/tag/0.1.6) (formerly MemGPT). |
| **Mem0** | `v0.0.86` | 2023-10-30 | GitHub Release | Earliest release returned by the paginated [`mem0ai/mem0` Releases API](https://github.com/mem0ai/mem0/releases/tag/v0.0.86). |
| **Graphiti** | `v0.1.0` | 2024-08-27 | GitHub Release | Initial public release tag for [`getzep/graphiti`](https://github.com/getzep/graphiti/releases/tag/v0.1.0). |
| **Supermemory** | `supermemory@0.0.0` | 2025-04-12 | npm Release | Initial public client package published to npm registry. *(First server prerelease: `server-v0.0.1-rc.2` on 2026-05-31)*. |
| **MemOS** | `v0.1.12` | 2025-07-06 | Tag-only | First verifiable Git tag on [`MemTensor/MemOS`](https://github.com/MemTensor/MemOS/tags). |
| **LangGraph** | `v0.0.3` | *Unestablished* | Tag-only | Early tag lineage (`v0.0.3`) present on GitHub; exact release date is unestablished in evidence. |

---

## 2. Major Release Milestones Across All Projects

The following list details the key architectural and product milestones across all projects in chronological order from earliest to latest.

- **2023-10-08 — Cognee (`0.0.1`)**: First verifiable public GitHub Release.
- **2023-10-26 — Letta (`0.1.6`)**: Earliest verifiable GitHub Release.
- **2023-10-30 — Mem0 (`v0.0.86`)**: Earliest verifiable GitHub Release.
- **2023-11-09 — Mem0 (`v0.1.0`)**: First semver 0.1 line release.
- **2024-01-30 — Letta (`0.3`)**: Verifiable GitHub Release in the 0.3 line.
- **2024-10-15 — Letta (`0.5.0`)**: Verifiable GitHub Release in the 0.5 line.
- **2024-12-04 — Letta (`0.6.0`)**: Verifiable GitHub Release in the 0.6 line.
- **2025-04-12 — Supermemory (`supermemory@0.0.0`)**: Initial npm package release establishing the JS/TS client API.
- **2025-05-11 — Supermemory (`supermemory@3.0.0-alpha.0`)**: Initial 3.0 alpha client line.
- **2025-06-27 — Graphiti (`v0.14.0`)**: Introduced search filters, exclusion entity types, full-text fixes, and UV package manager migration.
- **2025-07-06 — MemOS (`v0.1.12`)**: First verifiable public Git tag for the hybrid memory operating system architecture.
- **2025-07-07 — Graphiti (`v0.16.0`)**: Introduced bulk graph ingestion pipeline.
- **2025-07-23 — Graphiti (`v0.18.0`)**: Search-reranker scores exposed in return structures; multi-tenant `group_id` filtering fixes.
- **2025-08-07 — MemOS (`v1.0.0`)**: Milestone 1.0 architecture tag line.
- **2025-09-03 — Graphiti (`v0.20.0`)**: Removed legacy parallel runtime option; graph search efficiency rework.
- **2025-09-21 — Supermemory (`supermemory@3.1.0`)**: Stable 3.x client package milestone.
- **2025-09-24 — MemOS (`v1.1.0`)**: Milestone 1.1 architecture tag line.
- **2025-10-06 — Graphiti (`v0.22.0`)**: OpenTelemetry observability added; prompt and token usage optimizations.
- **2025-12-20 — Supermemory (`supermemory@4.0.0`)**: Major 4.0 client package line release.
- **2025-12-24 — MemOS (`v2.0.0`)**: 2.x tag; exact architecture milestone is not established by tag evidence alone.
- **2026-01-16 — Graphiti (`v0.26.0`)**: Sagas execution framework support and custom entity extraction instructions.
- **2026-02-17 — Graphiti (`v0.28.0`)**: Major GraphDriver operational interface update.
- **2026-03-10 — LangGraph (`1.1.0`)**: Typed opt-in v2 `GraphOutput`/`StreamPart` behavior; the exact first-public date of `1.0.0` remains unestablished.
- **2026-04-11 — Cognee (`v1.0.0`)**: Major-version GitHub Release.
- **2026-04-16 — Mem0 (`v2.0.0`)**: Major Python v2.0 breaking release: cutover to single-pass ADD-only pipeline, hybrid vector/BM25 retrieval, and the `search()`/`get_all()` filter migration. *(TS SDK `ts-v3.0.0` published concurrently)*.
- **2026-05-16 — Cognee (`v1.1.0`)**: GitHub Release.
- **2026-06-10 — Supermemory (`server-v0.0.1` / `server-v0.0.2`)**: First stable self-hosted binary server releases.
- **2026-06-21 — Cognee (`v1.2.0`)**: Ingestion and relational graph mapping feature release.
- **2026-07-09 — MemOS (`v2.0.23`)**: Material GitHub release introducing L3-specific LLM slot, CJK retrieval optimization, and lightweight memory evolution controls.
- **2026-07-12 — Cognee (`v1.3.0`)**: GitHub Release; its placeholder body does not establish a specific milestone.
- **2026-07-17 — Cognee (`v1.4.0`)**: GitHub Release; its placeholder body does not establish a specific milestone.

---

## 3. Active Window Material Releases (2026-03-24 to 2026-07-24)

Below is every material release and tag recorded across the seven project notes within the 4-month active research window (2026-03-24 through 2026-07-24). Releases occurring on the same calendar date are grouped together.

### 2026-03-26
- **Mem0 `v1.0.8`** — *GitHub Release & Tag*. Pre-v2 patch release.


### 2026-03-27
- **MemOS `v2.0.11`** — *Tag-only*. Maintenance release in v2.0 series.

### 2026-03-28
- **Mem0 `v1.0.9`** — *GitHub Release & Tag*. Pre-v2 patch release.

### 2026-03-30
- **Cognee `v0.5.6`** — *GitHub Release*. Minor release in pre-1.0 series.

### 2026-03-31
- **Letta `0.16.7`** — *GitHub Release*. Verifiable release in 0.16 line.

### 2026-04-01
- **Mem0 `v1.0.10`** — *GitHub Release & Tag*. Pre-v2 patch release.


### 2026-04-03
- **Cognee `v0.5.7`** — *GitHub Release*. Minor release in pre-1.0 series.
- **Supermemory `supermemory@4.21.0`** — *npm Release*. Feature update for JS/TS client integration.

### 2026-04-06
- **Mem0 `v1.0.11`** — *GitHub Release & Tag*. Final pre-v2 patch release returned on page 1 of Releases API.

### 2026-04-07
- **Cognee `v0.5.8`** — *GitHub Release*. Minor release.
- **MemOS `v2.0.12`** — *Tag-only*. Core and OpenClaw plugin update.

### 2026-04-08
- **Cognee `v0.5.8rc1`** — *Prerelease*. Release candidate for v0.5.8 line.

### 2026-04-09
- **Cognee `v0.5.4.dev3`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.
- **Cognee `v0.5.7.dev0`** — *Prerelease*. Development build.

### 2026-04-10
- **Cognee `v0.5.5.dev1`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.
- **MemOS `v2.0.13`** — *Tag-only*. Core maintenance release.

### 2026-04-11
- **Cognee `v1.0.0.dev0`** — *Prerelease*. Development build preceding 1.0.0.
- **Cognee `v1.0.0`** — *GitHub Release*. Major 1.0.0 milestone release.

### 2026-04-13
- **Mem0 `v2.0.0b0`** — *Prerelease (Tag & Release)*. v2 beta initial release.

### 2026-04-14
- **Cognee `v1.0.1.dev0`** — *Prerelease*. Development build.
- **Mem0 `v2.0.0b1`** — *Prerelease (Tag & Release)*. v2 beta follow-up.

### 2026-04-15
- **Cognee `v1.0.1.dev1`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.

### 2026-04-16
- **Cognee `v1.0.1.dev2`** — *Prerelease*. Development build.
- **Cognee `v1.0.1.dev3`** — *Prerelease*. Development build.
- **Mem0 `v2.0.0`** — *GitHub Release & Tag*. Major Python breaking release v2.0.0 (cutover to single-pass ADD-only, hybrid retrieval, and the `search()`/`get_all()` filter migration).
- **Mem0 `ts-v3.0.0`** — *GitHub Release & Tag*. TypeScript SDK v3.0.0 cutover in same monorepo.
- **Mem0 `v2.0.0b2`** — *GitHub Release & Tag*. Final v2 beta release.

### 2026-04-18
- **Cognee `v1.0.1`** — *GitHub Release*. Patch release.

### 2026-04-21
- **Cognee `v1.0.1.dev4`** — *Prerelease*. Development build.

### 2026-04-22
- **Cognee `v1.0.2`** — *GitHub Release*. Patch release.

### 2026-04-23
- **MemOS `v2.0.14`** — *Tag-only*. Core maintenance release.

### 2026-04-24
- **Cognee `v1.0.3`** — *GitHub Release*. Patch release.

### 2026-04-25
- **Cognee `v1.0.4.dev0`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.
- **Mem0 `v2.0.1`** — *GitHub Release & Tag*. Post-cutover patch update.

### 2026-04-27
- **Graphiti `v0.29.0`** — *GitHub Release*. Major feature release: combined node+edge extraction, batched extraction, saga API, Kuzu schema migration.

### 2026-05-03
- **Cognee `v1.0.4`** — *GitHub Release*. Patch release.
- **Cognee `v1.0.5`** — *GitHub Release*. Patch release.

### 2026-05-05
- **Cognee `v1.0.6`** — *GitHub Release*. Patch release.
- **Cognee `v1.0.7`** — *GitHub Release*. Patch release.

### 2026-05-06
- **Cognee `v1.0.8`** — *GitHub Release*. Patch release.

### 2026-05-07
- **Mem0 `v2.0.2`** — *GitHub Release & Tag*. Maintenance release.

### 2026-05-08
- **Cognee `v1.0.9`** — *GitHub Release*. Patch release.

### 2026-05-11
- **MemOS `v2.0.15`** — *Tag-only*. Core maintenance release.

### 2026-05-12
- **Cognee `v1.1.0.dev0`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.

### 2026-05-13
- **Cognee `v1.1.0.dev1`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.

### 2026-05-14
- **Letta `0.16.8`** — *GitHub Release*. Latest published release: security fix switching sandbox/server tool-result serialization from `pickle` to `JSON`.

### 2026-05-16
- **Cognee `v1.1.0`** — *GitHub Release*. Major feature release.

### 2026-05-19
- **MemOS `v2.0.16`** — *Tag-only*. Core maintenance release.

### 2026-05-21
- **Graphiti `v0.29.1`** — *GitHub Release*. Extraction quality guards, saga event-time watermark, FalkorDB Docker mount fix.

### 2026-05-22
- **Cognee `v1.1.1.dev0`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.

### 2026-05-26
- **Mem0 `v2.0.3`** — *GitHub Release & Tag*. Patch update.
- **MemOS `v2.0.17`** — *Tag-only*. Core maintenance release.

### 2026-05-27
- **Mem0 `v2.0.4`** — *GitHub Release & Tag*. Patch update.

### 2026-05-29
- **Cognee `v1.1.1`** — *GitHub Release*. Patch release.

### 2026-05-30
- **Cognee `v1.1.2`** — *GitHub Release*. Patch release.

### 2026-05-31
- **Supermemory `server-v0.0.1-rc.2`** — *Prerelease (GitHub Release)*. First verifiable self-hosted server binary prerelease.

### 2026-06-04
- **Supermemory `server-v0.0.1-rc.8`** — *Prerelease (GitHub Release)*. Server stabilization prerelease.

### 2026-06-08
- **Graphiti `v0.29.2`** — *GitHub Release*. Embedded FalkorDB support, FalkorDB fixes, Kuzu driver deprecation, MCP server parity.

### 2026-06-10
- **Mem0 `v2.0.5`** — *GitHub Release & Tag*. Patch update.
- **Supermemory `server-v0.0.1`** — *GitHub Release*. First stable self-hosted binary server release.
- **Supermemory `server-v0.0.2`** — *GitHub Release*. Follow-up stable binary server release.

### 2026-06-12
- **MemOS `v2.0.19`** — *Tag-only*. Core maintenance release.

### 2026-06-13
- **Supermemory `server-v0.0.3`** — *GitHub Release*. Patch release for server binary.
- **Mem0 `v2.0.6`** — *GitHub Release & Tag*. Maintenance update.

### 2026-06-17
- **Cognee `v1.2.0.dev0`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.
- **Mem0 `v2.0.7`** — *GitHub Release & Tag*. Patch update.

### 2026-06-18
- **Cognee `v1.1.3`** — *GitHub Release*. Patch release in v1.1 series.
- **LangGraph `1.2.6`** — *GitHub Release & Tag*. Fixed nested subgraph parent `checkpoint_ns` inheritance regression and v3 stream abort cancellation.
- **MemOS `v2.0.20`** — *Tag-only*. Core context rendering search-pipeline hooks released.

### 2026-06-19
- **Cognee `v1.2.0.dev1`** — *Prerelease*. Development build.

### 2026-06-21
- **Cognee `v1.2.0`** — *GitHub Release*. Feature release.
- **Cognee `v1.2.1`** — *GitHub Release*. Immediate patch release.

### 2026-06-24
- **Mem0 `v2.0.8`** — *GitHub Release & Tag*. Patch release.

### 2026-06-25
- **Cognee `v1.2.2.dev0`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.

### 2026-06-26
- **Cognee `v1.2.2`** — *GitHub Release*. Patch release.

### 2026-06-27
- **Mem0 `v2.0.10`** — *GitHub Release & Tag*. Patch release (note: `v2.0.9` is omitted from the paginated GitHub Releases API).

### 2026-06-30
- **LangGraph `1.2.7`** — *GitHub Release & Tag*. `DeltaChannel` overwrite-supersedes TS snapshot; JSON-roundtrip `'Overwrite'`; exit-mode task UUID fix.

### 2026-07-01
- **Mem0 `v2.0.11`** — *GitHub Release & Tag*. Patch release.

### 2026-07-03
- **MemOS `v2.0.22`** — *Tag-only*. Broad local-plugin reliability and memory/export performance fixes. (Note: `v2.0.21` omitted in evidence).

### 2026-07-06
- **Cognee `v1.2.2.dev1`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.
- **LangGraph `1.2.8`** — *GitHub Release & Tag*. Fresh-thread `updateState` `DeltaChannel` fix (forces snapshot rather than stub checkpoint).

### 2026-07-07
- **Cognee `v1.2.2.dev2`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.
- **Cognee `v1.2.2.dev3`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.
- **Cognee `v1.2.2.dev4`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.

### 2026-07-09
- **MemOS `v2.0.23`** — *GitHub Release*. Material release featuring L3-specific LLM slot, CJK retrieval optimization, and lightweight evolution controls.

### 2026-07-10
- **LangGraph `1.2.9`** — *GitHub Release & Tag*. `DeltaChannel` `updateState` metadata/counter fix. Current core engine release.
- **Supermemory `server-v0.0.4`** — *GitHub Release*. Expanded memory extraction, time-aware search, and profile buckets.
- **Supermemory `server-v0.0.5`** — *GitHub Release*. Pluggable local/remote embeddings and embedding plan persistence.

### 2026-07-12
- **Cognee `v1.3.0`** — *GitHub Release*. Placeholder body does not establish a specific milestone.

### 2026-07-13
- **Mem0 `v2.0.12`** — *GitHub Release & Tag*. Maintenance release.

### 2026-07-17
- **Cognee `v1.4.0`** — *GitHub Release*. Placeholder body does not establish a specific milestone.

### 2026-07-19
- **MemOS `v2.0.24`** — *Tag-only*. CI/docs/local-plugin packaging maintenance.
- **Supermemory `server-v0.0.6`** — *GitHub Release*. Support added for self-hosted Windows binaries.

### 2026-07-20
- **Cognee `v1.4.0.dev0`** — *GitHub Release (dev-named build; not marked prerelease by GitHub)*.
- **Supermemory `supermemory@4.24.2`** — *npm Release*. Published JS/TS client package update.

### 2026-07-22
- **Cognee `v1.4.0.dev1`** — *Prerelease*. Development build.
- **Mem0 `v2.0.13`** — *GitHub Release & Tag*. Reset/backend provider fixes; latest published Python release.
- **Supermemory `server-v0.0.7-rc.2`** — *Prerelease (GitHub Release)*. Offloaded step data for >128KiB inputs and hardened shutdown lifecycle.

### 2026-07-24
- **MemOS `v2.0.25`** — *Tag-only*. Latest snapshot tag. Packaging, store stability, and batch-reflection scoring maintenance (reverted in same release).

---

## 4. Release-Cadence Observations

Without evaluating software quality, developer productivity, or project stability, the recorded primary evidence reveals distinct release practices across the projects during the active window:

1. **High-Frequency Granular Tagging (Cognee)**: Cognee publishes frequent dev-named releases, with prerelease status determined by each GitHub Release object, and frequent micro-patch releases (for example six distinct releases between 2026-05-03 and 2026-05-08).
2. **Post-Major-Break Rapid Patching (Mem0)**: Following the architectural cutover to `v2.0.0` on 2026-04-16, Mem0 published twelve subsequent GitHub patch releases (`v2.0.1` through `v2.0.13`, with no `v2.0.9` GitHub Release) over the active window.
3. **Dual-Track Monorepo Versioning (Supermemory)**: Supermemory maintains separate release cadences for its client SDK (published via npm) and its self-hosted binary server (published via GitHub Releases), introducing server prereleases (`rc`) prior to stable binary version tags.
4. **Git Tag-Dominant Distribution (MemOS)**: MemOS relies primarily on Git tags (`v2.0.11` through `v2.0.25`) for public version tracking, using official GitHub Releases only for major feature milestones such as `v2.0.23`.
5. **Low-Frequency Formal Releasing (Letta & Graphiti)**: Letta and Graphiti publish formal GitHub Releases less frequently in the active window (for example Graphiti `v0.29.0`–`v0.29.2` and Letta `0.16.7`–`0.16.8`); this cadence observation does not infer release-body milestones beyond the evidence in their notes.
