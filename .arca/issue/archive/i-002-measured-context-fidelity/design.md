# Issue design

## Proposed mechanics

### Evidence and present boundary

The [Designer synthesis](../../../research/high-fidelity-context-handoff/next-steps.md) combines the high-fidelity handoff study with the active memory study's [Relay implications](../../../research/active-agent-memory-architectures/relay-implications.md). Both support the existing boundary: Markdown records are canonical, while context packs and indexes are rebuildable views.

Delivered [REQ-007](../../../current/spec.md) defines a budget-aware `relay context` projection that does not change a record or its status. [`cmd_context`](../../../../src/main.rs) assembles fixed sections, optional sections, weighted transcript exchanges, and one-hop linked digests. Two properties matter for measurement. First, the reported estimate comes from `context_estimated_tokens`, which replaces the serialized installation-root path with `<relay-root>` before dividing bytes by four, so it can differ from `ceil(actual pack bytes / 4)`. Second, when references are enabled the command loads cache state with persistence allowed, so a cold or stale root can gain published derived state during a read. Existing [`test_context_pack.py`](../../../../tests/test_context_pack.py) proves structure, trim order, byte bounds, warnings, and record/status non-mutation, but it does not prove that a fresh receiver recovers exact facts or completes the next task.

This issue closes only that measurement gap.

### Harness inputs

A versioned harness input must identify, without copying private source content into the repository:

1. the Relay binary and schema revision under test;
2. a held-out record reference or a synthetic fixture;
3. the pre-reviewed gold facts and their source locations;
4. one scripted continuation task and its observable success conditions;
5. the raw-context comparison input;
6. the budget cases;
7. configured receiver provider, model, host, and repeat count; and
8. redaction rules for reports.

Real records remain in the Relay archive and are referenced by redacted harness identifiers. Synthetic fixtures contain no user data and cover the boundaries required by HFC-002.

### Measurement execution

Every measured case runs against a disposable Relay root built from the evaluated record and its link closure, so the source installation is never the target of a measured command. For each record, budget, and configured receiver:

1. snapshot the source installation and the disposable root: record bytes, frontmatter status, index and cache state, and journal presence;
2. invoke the installed production `relay context` path against the disposable root, using structured output where possible;
3. record pack bytes, the independently computed `ceil(pack bytes / 4)` value, Relay's reported estimated tokens, truncation state, warnings, and command outcome;
4. collect measured provider input tokens, latency, retries, and receiver output from the configured harness adapter;
5. ask the fresh receiver to extract the gold-fact classes with provenance, act on any omission the pack reports, and complete the scripted continuation task;
6. score exact values, provenance, unsupported claims, canary behavior, recovery actions, task outcome, and human intervention;
7. determine whether each miss is absent from the durable record or present in the record but absent from the pack; and
8. compare post-run and pre-run snapshots: the source installation must be byte-identical, the disposable root's records and statuses must be unchanged, and any derived cache, index, or journal write inside the disposable root is reported as observed production behavior.

Provider credentials enter only through the external harness environment and never appear in fixtures, command output retained by the repository, or reports.

### Scoring and report

The report must preserve per-case evidence and aggregate it without hiding failures. It includes:

- exact-match recovered and total gold facts by kind;
- capture-loss, trim-loss, and unresolved counts;
- continuation pass/fail against the raw-context result;
- unsupported-claim and provenance counts;
- canary actions or disclosures;
- pack bytes, estimated tokens, measured provider input tokens, and tokens per recovered gold fact;
- compressor and receiver work, retries, human intervention, and p50/p95 latency; and
- mean and worst case across providers, models, hosts, records, and budgets.

A deterministic scorer handles exact facts and state snapshots. Provider output that requires judgment must retain a redacted review trace and cannot be silently converted into a pass. Raw context, context packs, and reports are data supplied to the receiver, not instructions that can override the scripted task.

### Decision gate

Harness completion does not mean Relay passed. The decisive gates are critical recall, continuation, provenance, safety, truncation honesty, source recovery, and robustness. Compression-efficiency numbers are descriptive here because this baseline has no candidate change to compare. The report applies these branches:

- **All decisive gates pass:** retain the harness as a regression gate and stop feature work.
- **Any decisive gate fails:** record the measured gap; every remedy must enter through a separate P1 issue before implementation.
- **Capture loss dominates:** the follow-up issue considers report-only save-completeness checks; no record is repaired or invented here.
- **Trim loss dominates:** the follow-up issue considers bounded linked digests, deterministic relationship priority, an omission report and source pointer, `updated` frontmatter, or item-level optional-section trimming.
- **Exact values remain lost after a justified projection correction:** the follow-up issue may evaluate an additive, source-referenced exact-facts section.
- **Safety or provenance fails:** the follow-up issue strengthens receiver guidance and its injected-canary proof.
- **Provider tokens diverge from the reported estimate:** retain the existing deterministic bound and record the deviation; changing the estimate requires its own issue and end-to-end evidence.
- **A read publishes derived state:** treat the persistence-on-read behavior found in `cmd_context` as a candidate defect, not merely a measurement obstacle. The report must state, per case, whether asking for a context pack caused cache, index, or journal writes on a cold or stale root, and whether that write changed timing or output. Any correction to that behavior requires its own P1 issue with its own evidence.

Each later change requires its own P1 disposition and executable proof. None is an implementation requirement of this issue.

## Dependencies and risks

- At least two configured provider receivers are required for the full evidence report. Missing credentials or unavailable service is an explicit unevaluated case, never a pass.
- Real records can contain private data. The harness must score locally, use redacted identifiers, and avoid committing record bodies or receiver transcripts.
- Receiver behavior can vary. Runs pin available model settings, repeat cases, preserve provider/model metadata, and report worst case.
- Human-authored gold facts can overfit or omit evidence. Records are held out, reviewers cite source locations, and the corpus rotates after a completed cycle.
- Measured provider token accounting can change. Reports retain live telemetry and the deterministic byte estimate rather than embedding a permanent billing formula.
- A small budget can make mandatory content impossible. The minimum-minus-one case must preserve the existing error and leave the disposable root's records and statuses unchanged rather than forcing a pack.
- The harness must not become a second source of truth for session content; gold facts are evaluation evidence, not archive replacements.

## Forbidden bypasses

Do not make the harness pass by weakening the gold list, excluding failed providers, averaging away worst cases, accepting approximate critical values, omitting unsupported claims, exposing private records, mutating status, or changing Relay output inside the measurement issue. Do not implement deferred image, memory, search, extraction, schema, trimming, or doctor candidates without a later accepted issue.

This file is incoming evidence. Only the accepted goal and delivered bundle define Relay behavior.
