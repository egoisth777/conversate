# Advisory next steps for Relay

## Standing

This is advisory research output derived from [Relay implications](relay-implications.md). It does not change delivered Relay authority. Any adoption requires a new issue through the P1 route in [`.arca/index.md`](../../index.md).

## Priority order

1. **Now — prove interruption convergence.** Add the mutation-boundary interruption matrix: replay after each boundary must converge, and a second replay must be idempotent.
2. **Now — prove derived equivalence.** Gate agreement among the cached path, `RELAY_NO_CACHE=1`, and `rebuild-index --full`; retain byte-stable, ID-sorted `index.jsonl` output.
3. **Now — prove deletion completeness and truthful outcomes.** Verify removal or rename leaves no postings, cache rows, or reverse references; assert each successful mutation reports an observable effect or an explicit no-op.
4. **Next — expose recovery and enforce bounds.** Have doctor report journal replay and derived rebuilds; document and test body-fallback and linked-digest caps plus deterministic trim order.
5. **Next — harden format and import transitions.** Preflight cache-format versions by building new generations from the archive, never migrating derived state in place; prove legacy import idempotence and stable collision reporting.
6. **Later — gate any new writer or store.** Before design work on multi-writer access or a second independently written store, require single-commit-point publication or a demonstrated reconcile-from-archive path.

## Non-goals

This study does not recommend adding a relational store, graph database, vector store, owned embeddings, LLM extraction pipeline, or owned embedding-migration machinery to Relay.
