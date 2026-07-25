# Ticket: t-04-hook-production-fault-seam

```yaml
ticket-id: t-04-hook-production-fault-seam
behavior-refs:
  - "[REQ-011](../../goal/spec.md#req-011--deterministic-hook-behavior-on-supported-platforms)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-HOOK-PLATFORM"
  - "T-HOOK-OUTCOMES"
dependencies:
  - "t-02-hook-counter-outcome"
status: done
```

## Scope

Provide fault injection and multi-session coverage that run through the installed production hook path without any test-only behavioral divergence.

Reason: Fault behavior proven only through a test double would not prove the shipped path.

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-HOOK-PLATFORM-SESSIONS | REQ-011 | two sessions with distinct production counter and lock paths | `cargo test --bin relay hook_runtime` | one session lock or failure cannot change the other session result |
| T-HOOK-PLATFORM-PATH | REQ-011 | the installed hook entry point with injected faults | `cargo test --bin relay hook_runtime` | the same production persistence protocol is exercised and no cfg(test) behavioral path is added |

## P5 proof and review

- Test result: python -m pytest tests/test_hook_increments.py: 4 passed against the built binary; cargo test --bin relay: 30 passed including distinct-session isolation and the Windows share-mode injection.
- Review note: Coverage runs through the shipped `relay hook` command and real filesystem faults; no cfg(test) behavioral path was added. The Unix permission-based injection is written but unevaluated on this Windows host.
- Residual reverse reference: [r-relay-11-hook-platform-determinism](../../residual/r-relay-11-hook-platform-determinism.md)
