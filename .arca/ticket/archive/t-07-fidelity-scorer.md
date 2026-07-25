# Ticket: t-07-fidelity-scorer

```yaml
ticket-id: t-07-fidelity-scorer
behavior-refs:
  - "[REQ-012](../../goal/spec.md#req-012--measured-context-fidelity-evidence)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-FIDELITY-RUN"
dependencies:
  - "t-06-fidelity-disposable-root-runner"
status: done
```

## Scope

Implement the deterministic gold-fact scorer and loss attribution: exact-match recall by fact kind, provenance checking, unsupported-claim counting, and capture-loss versus trim-loss classification with an explicit unresolved class.

Reason: Loss attribution decides which future remedy is even eligible, so it must be deterministic.

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-FIDELITY-SCORE-EXACT | REQ-012 | receiver answers with known correct and corrupted values | `python -m pytest tests/test_context_fidelity_scoring.py` | only exact matches count as recovered and near-misses are reported as misses |
| T-FIDELITY-SCORE-ATTRIBUTION | REQ-012 | a fact absent from the record and a fact trimmed from the pack | `python -m pytest tests/test_context_fidelity_scoring.py` | the first is capture loss, the second is trim loss, and an unproven cause stays unresolved |

## P5 proof and review

- Test result: python -m pytest tests/test_context_fidelity_scoring.py: 13 passed.
- Review note: Exact match after whitespace and case normalization; a near miss is a miss and aliases count only when declared. Loss attribution is capture, trim, receiver, or unresolved, with unresolved used whenever the evidence cannot prove a stage. Rollup reports the worst cell and refuses to publish a mean. Mutation checks: always-present matching fails 7 checks; a best-cell rollup fails the worst-cell check.
- Residual reverse reference: [r-relay-12-context-fidelity-evidence](../../residual/r-relay-12-context-fidelity-evidence.md)
