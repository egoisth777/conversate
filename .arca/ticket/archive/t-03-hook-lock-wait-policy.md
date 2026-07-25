# Ticket: t-03-hook-lock-wait-policy

```yaml
ticket-id: t-03-hook-lock-wait-policy
behavior-refs:
  - "[REQ-009](../../goal/spec.md#req-009--lossless-session-turn-counting)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-HOOK-LOSSLESS"
  - "T-HOOK-REMINDER"
dependencies:
  - "t-02-hook-counter-outcome"
status: done
```

## Scope

Replace the fixed 32-attempt, 5 ms lock window with a bounded wait policy that does not lose an accepted submission under contention, and emit the tenth-turn reminder only for committed counts.

Reason: Correctness must not depend on a magic retry count or scheduler timing; contention is recoverable and must never be reported as loss.

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-HOOK-LOSSLESS-CONCURRENT | REQ-009 | a generated set of concurrent accepted submissions for one session | `cargo test --bin relay hook_runtime` | durable count equals the number of submissions that were not reported as explicit failures, with the expected total derived from the generated set |
| T-HOOK-REMINDER-BOUNDARY | REQ-009 | initial counts and submission ranges spanning several tenth-turn boundaries | `cargo test --bin relay hook_runtime` | exactly one reminder per committed count divisible by ten and none for other committed counts |

## P5 proof and review

- Test result: cargo test --bin relay: 30 passed with 2, 5, 16, and 33 concurrent workers and tenth-turn boundaries at initial counts 0, 5, 9, 17, and 95. python -m pytest tests/test_hook_increments.py: 4 passed. Mutation check: a 1 microsecond wait budget loses 15 of 16 installed-path submissions and fails the suite.
- Review note: The fixed 32-attempt window became a time budget with exponential backoff, so recoverable contention waits instead of dropping a submission.
- Residual reverse reference: [r-relay-09-lossless-turn-counting](../../residual/r-relay-09-lossless-turn-counting.md)
