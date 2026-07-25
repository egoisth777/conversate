# Residual record

```yaml
residual-id: r-relay-09-lossless-turn-counting
goal-requirement-ref: "[REQ-009](../goal/spec.md#req-009--lossless-session-turn-counting)"
frozen-goal-revision: g-001
implementation-revision: "28251ea plus goal g-001 hook work"
status: satisfied
concrete-evidence-refs:
  - "cargo test --bin relay: concurrent_increments_are_not_lost passes at 2, 5, 16, and 33 workers"
  - "cargo test --bin relay: reminders_follow_committed_tenth_turns passes at initial counts 0, 5, 9, 17, 95"
  - "python -m pytest tests/test_hook_increments.py: 4 passed through the installed binary"
  - "mutation check: a 1 microsecond lock budget loses 15 of 16 installed-path submissions and fails the suite"
required-test-refs:
  - T-HOOK-LOSSLESS
  - T-HOOK-REMINDER
classification-rationale: "Every accepted submission now commits or reports an explicit failure, the expected total is derived from reported outcomes rather than a fixed worker count, and the checks are proven sensitive by mutation."
```
