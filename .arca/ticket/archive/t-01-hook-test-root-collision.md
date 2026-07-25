# Ticket: t-01-hook-test-root-collision

```yaml
ticket-id: t-01-hook-test-root-collision
behavior-refs:
  - "[REQ-011](../../goal/spec.md#req-011--deterministic-hook-behavior-on-supported-platforms)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-HOOK-PLATFORM"
dependencies:
  - "none"
status: done
```

## Scope

Give the hook test temporary root a collision-free identity so parallel Rust tests cannot share a directory on coarse Windows clocks.

Reason: Windows SystemTime granularity lets two tests derive the same nanosecond suffix, so `fs::create_dir` panics and hides the real contract failure.

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-HOOK-PLATFORM-ROOT | REQ-011 | many parallel test roots created in one clock tick | `cargo test --bin relay hook_runtime` | every created root path is unique and no test panics on AlreadyExists |

## P5 proof and review

- Test result: cargo test --bin relay: 30 passed. The new `test_roots_are_unique_under_parallel_creation` reproduced the collision at 2 of 15 suite runs before the fix and 0 of 30 after it.
- Review note: Test roots now carry a process id and an atomic sequence, so a coarse Windows clock can no longer make two parallel tests share a directory.
- Residual reverse reference: [r-relay-11-hook-platform-determinism](../../residual/r-relay-11-hook-platform-determinism.md)
