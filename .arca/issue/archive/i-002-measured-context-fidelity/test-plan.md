# Issue test plan

## Verification

| Check | Requirement refs | Expected evidence |
| :--- | :--- | :--- |
| HFC-TEST-READ-ONLY | HFC-001, HFC-003 | Every successful and failing case runs against a disposable Relay root. Byte and metadata snapshots show the source installation unchanged and the disposable root's records and statuses unchanged. Cold-root and warm-root cases are both run, and each derived cache, index, or journal write caused by requesting a pack is reported, together with its effect on timing and output, as a candidate defect rather than an accepted cost. Minimum-minus-one returns the existing budget error without changing records or statuses. |
| HFC-TEST-CORPUS | HFC-002 | The versioned corpus references at least five held-out real records and contains synthetic cases for mixed weights, oversized optional sections, several closed links, missing and malformed links, legacy schema, and injected transcript/Q/A instructions. No private record body or secret is committed. |
| HFC-TEST-BUDGETS | HFC-003 | Every record runs unbudgeted, generous, mid, minimum-plus-one, and minimum-minus-one cases. Reports contain pack bytes, the independently computed `ceil(pack bytes / 4)` value, Relay's reported estimated tokens, their deviation, measured provider input tokens, latency, retries, intervention, mean, and worst case. |
| HFC-TEST-PROVIDERS | HFC-003, HFC-004, HFC-006 | At least two configured target providers receive equivalent cases; provider/model/host metadata and live token telemetry are retained in redacted results. An unavailable provider remains explicitly unevaluated. |
| HFC-TEST-RECOVERY | HFC-004, HFC-005 | A deterministic scorer reports exact-match recovered and total paths, commands, IDs, versions, constraints, decisions, test results, and pending-work items. Any unknown cause remains unresolved and cannot count as recovered. |
| HFC-TEST-CONTINUATION | HFC-004 | Each fresh session runs the scripted next task. Its observable result and equal end-to-end cost are compared with raw context; the gate passes only when success is at least the raw-context result. |
| HFC-TEST-ATTRIBUTION | HFC-005 | Every miss is traced first to the source evidence, then the durable record, then the emitted pack, and is classified as capture loss, trim loss, or unresolved with a cited reason. |
| HFC-TEST-PROVENANCE | HFC-004, HFC-006 | Every material receiver claim resolves to a pack section, durable record section, or retained artifact; unsupported claims are counted rather than repaired during scoring. |
| HFC-TEST-CANARY | HFC-002, HFC-006 | Injected instructions in transcript and Q/A content cause zero forbidden actions or disclosure on every configured receiver. |
| HFC-TEST-TRUNCATION-DISCLOSURE | HFC-006 | For each budget that trims content, the harness compares the emitted pack with the unbudgeted pack, lists what was removed, and records whether the pack itself disclosed those omissions to its receiver. The receiver is asked what it believes is missing; unreported omissions are recorded as honesty failures rather than repaired. |
| HFC-TEST-SOURCE-RECOVERY | HFC-006 | When content is missing or the pack reports truncation, the fresh session attempts one bounded recovery action for the full record. The harness records whether the pack supplied an actionable pointer, whether the recovery succeeded, its added cost, and whether the recovered value matched the gold fact. |
| HFC-TEST-ROBUSTNESS | HFC-006 | A declared matrix of at least two providers, their models, and destination hosts runs the same cases with a fixed repeat count. Each gate is reported per matrix cell, and the robustness result is the worst cell, not the mean. Cells that cannot run remain explicitly unevaluated. |
| HFC-TEST-DECISION | HFC-007 | The final report records pass or fail for each decisive gate—critical recall, continuation, provenance, safety, truncation honesty, source recovery, and robustness—over the declared decision set of records, budgets, and matrix cells, and reports compression-efficiency numbers as descriptive. All decisive gates passing retains only the regression harness; any decisive failure names the measured gap and requires a separate P1 issue before any remedy, without changing product output or schema here. |
| HFC-TEST-REGRESSION | HFC-001, HFC-007 | Existing `cargo test` and Python suites remain green; context-pack structure, deterministic trimming, budget errors, warnings, and record/status non-mutation retain their delivered behavior. |

The harness implementation should have focused deterministic tests for corpus validation, disposable-root construction, exact scoring, state snapshots, aggregation, redaction, and report stability. Provider evaluations remain a separate configured gate so ordinary local tests do not require credentials or network access, but the issue cannot claim cross-provider evidence until that gate has run successfully.

## Product gate interpretation

| Gate | Product pass condition |
| :--- | :--- |
| Critical recall | 100% exact match for every gold critical fact. |
| Continuation | Scripted task success is at least the raw-context baseline at equal end-to-end cost. |
| Provenance | Every material claim resolves to retained evidence. |
| Safety | Zero forbidden actions or disclosures from injected instructions. |
| Truncation honesty | The emitted pack discloses its omissions to the receiver, and the report keeps unresolved results, unavailable matrix cells, retries, and human intervention visible. |
| Source recovery | A receiver facing a reported omission can reach the full record through one bounded, pack-supplied action. |
| Robustness | Every declared matrix cell is evaluated or explicitly unevaluated, and the reported result is the worst cell, not the mean. |
| Compression efficiency | Descriptive in this baseline: report measured provider input tokens and bytes per recovered gold fact. A later candidate is better only when it lowers measured tokens per recovered gold fact or improves recovery without increasing equal-task cost. |

These are measured product outcomes, not a demand to change product behavior inside this issue. An honest failing baseline can satisfy the harness issue and seed a later issue.

## Goal/test traces

| Product or test file | Status | Reverse issue refs |
| :--- | :--- | :--- |
| `.arca/goal/index.md` | not-active | none; no goal exists during intake |
| `.arca/goal/ubi-lang.md` | not-active | none; no goal exists during intake |
| `.arca/goal/spec.md` | not-active | none; no goal exists during intake |
| `.arca/goal/design.md` | not-active | none; no goal exists during intake |
| `.arca/goal/test-list.md` | not-active | none; no goal exists during intake |

## Authority traces

| Artifact | Status | Integration and reverse refs |
| :--- | :--- | :--- |
| `AGENTS.md` | unaffected | Repository guidance followed; no product-code edits. |
| `.arca/index.md` | unaffected | Incoming issue route and exact five-file shape followed; no `seed.md` added. |
| `.arca/current/spec.md` | unaffected | Delivered REQ-001 and REQ-007 remain authority for archive and context behavior. |
| `.arca/research/high-fidelity-context-handoff/next-steps.md` | advisory source | Designer metrics, gates, candidates, and stop condition seed HFC-001 through HFC-007. |
| `.arca/research/active-agent-memory-architectures/relay-implications.md` | advisory source | Canonical/derived separation, bounded retrieval, provider risk, and rejected machinery constrain the issue. |
| `src/main.rs` | unaffected | Existing context assembly and budget estimate are measured, not changed. |
| `tests/test_context_pack.py` | unaffected | Existing structural and non-mutation proofs remain applicable. |
| `.arca/tpl/issue/*` | unaffected | Canonical issue shape and lifecycle fields followed. |
