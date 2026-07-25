# Ticket: t-02-hook-counter-outcome

```yaml
ticket-id: t-02-hook-counter-outcome
behavior-refs:
  - "[REQ-010](../../goal/spec.md#req-010--explicit-hook-counter-outcomes)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-HOOK-OUTCOMES"
dependencies:
  - "t-01-hook-test-root-collision"
status: done
```

## Scope

Replace the `Option<u64>` result of `CounterStore::increment` with an explicit outcome carrying committed count, rejected input, failure before replacement, and uncertain durability after replacement, and report unreadable or malformed counter content instead of resetting it to zero.

Reason: A single empty answer cannot express four different results; the caller currently cannot tell "no reminder" from "your turn was lost".

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-HOOK-OUTCOMES-CLASSIFY | REQ-010 | counter files that are absent, valid, unreadable, and malformed | `cargo test --bin relay hook_runtime` | each case returns its distinct outcome and a malformed counter never republishes a lower value |
| T-HOOK-OUTCOMES-PRESERVE | REQ-010 | injected pre-replacement write failure | `cargo test --bin relay hook_runtime` | the previously published counter is byte-identical afterwards and the outcome is failure-before-replacement |
| T-HOOK-OUTCOMES-UNCERTAIN | REQ-010 | injected durability-sync failure after replacement | `cargo test --bin relay hook_runtime` | the outcome is uncertain and does not claim the prior state survived |

## P5 proof and review

- Test result: cargo test --bin relay: 30 passed, including outcome classification, quarantine, overflow, unreadable counter, stage mapping, and the Windows blocked-replacement injection. Mutation checks: swallowing a write failure and silently zeroing a malformed counter both fail the suite.
- Review note: `CounterOutcome` and `CounterFailure` replace the ambiguous `Option<u64>`; `atomic_io::write_atomic_staged` keeps the failing stage so replacement failure and durability uncertainty are no longer the same answer.
- Residual reverse reference: [r-relay-10-hook-counter-outcomes](../../residual/r-relay-10-hook-counter-outcomes.md)
