# Project selection

## Selection result

Snapshot from canonical GitHub repository and Releases APIs on 2026-07-24.

`open items` below is GitHub's repository-level `open_issues_count`, which may include pull requests. Project notes use the Issues API and exclude pull requests.

| Project | Canonical repository | Stars | Latest published release | Release date | Recent repository push | Open items | Decision |
| :--- | :--- | ---: | :--- | :--- | :--- | ---: | :--- |
| Mem0 | [`mem0ai/mem0`](https://github.com/mem0ai/mem0) | 61,615 | `v2.0.13` | 2026-07-22 | 2026-07-24 | 698 | Select: largest memory-first candidate and recently released |
| AutoGen | [`microsoft/autogen`](https://github.com/microsoft/autogen) | 59,941 | `python-v0.7.5` | 2025-09-30 | 2026-04-15 | 970 | Exclude: memory is a subsystem and no release in the requested recent window |
| CrewAI | [`crewAIInc/crewAI`](https://github.com/crewAIInc/crewAI) | 56,079 | `1.15.5` | 2026-07-20 | 2026-07-24 | 663 | Exclude: orchestration is primary; memory is optional |
| LlamaIndex | [`run-llama/llama_index`](https://github.com/run-llama/llama_index) | 51,067 | `v0.14.23` | 2026-06-24 | 2026-07-23 | 573 | Exclude from primary seven: broad document/RAG framework; retain as comparator |
| LangGraph | [`langchain-ai/langgraph`](https://github.com/langchain-ai/langgraph) | 38,055 | `1.2.9` | 2026-07-10 | 2026-07-22 | 641 | Select: independently inspectable checkpoint and store architecture |
| Cognee | [`topoteretes/cognee`](https://github.com/topoteretes/cognee) | 29,260 | `v1.4.0.dev0` | 2026-07-20 | 2026-07-24 | 609 | Select: memory-first graph/vector ingestion pipeline |
| Graphiti | [`getzep/graphiti`](https://github.com/getzep/graphiti) | 29,154 | `v0.29.2` | 2026-06-08 | 2026-07-24 | 434 | Select: distinct temporal knowledge-graph design |
| Supermemory | [`supermemoryai/supermemory`](https://github.com/supermemoryai/supermemory) | 28,589 | `server-v0.0.6` | 2026-07-19 | 2026-07-24 | 91 | Select: API-first memory/context engine |
| Letta | [`letta-ai/letta`](https://github.com/letta-ai/letta) | 23,943 | `0.16.8` | 2026-05-14 | 2026-07-22 | 51 | Select: agent-edited memory blocks and archival context |
| MemOS | [`MemTensor/MemOS`](https://github.com/MemTensor/MemOS) | 10,363 | `v2.0.25` | 2026-07-24 | 2026-07-24 | 76 | Select: self-evolving hybrid memory and skill reuse |

| Memary | [`kingjulio8238/Memary`](https://github.com/kingjulio8238/Memary) | 2,634 | No public GitHub release | — | 2024-10-22 | 14 | Exclude: inactive during the required window |

Cognee and Supermemory values in the **Latest published release** column come from the latest non-prerelease release endpoint. Their later prereleases are recorded in the project notes and release timeline.

## Why these seven

The final set contains six memory-first systems and one framework whose persistence design is independently inspectable:

1. Mem0 — extracted facts and multiple stores;
2. Letta — agent-managed in-context blocks;
3. Graphiti — temporal and bi-temporal graph;
4. Cognee — graph/vector memory pipeline;
5. Supermemory — memory/context API;
6. MemOS — hybrid memory operating system and reusable skills;
7. LangGraph — checkpointed execution state and cross-thread stores.

This is not a pure star ranking. A pure ranking would mostly select general agent frameworks and hide the architectural differences the research needs.

## Evidence boundaries

- Stars, releases, push dates, and counts are volatile observations.
- A repository push can be a branch or pull-request update; each project researcher must pin an actual source revision.
- Latest-release endpoints do not reveal first release. Project researchers must paginate releases/tags and avoid substituting repository creation date.
- Public issue reports are symptoms and claims, not automatically confirmed defects.

## API sources

For each repository:

- `https://api.github.com/repos/{owner}/{repo}`
- `https://api.github.com/repos/{owner}/{repo}/releases/latest`
- `https://api.github.com/repos/{owner}/{repo}/releases?per_page=100&page={n}`
- `https://api.github.com/repos/{owner}/{repo}/tags?per_page=100&page={n}`
- `https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page=100&page={n}`
