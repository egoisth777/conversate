# Residual record

```yaml
residual-id: r-relay-11-hook-platform-determinism
goal-requirement-ref: "[REQ-011](../goal/spec.md#req-011--deterministic-hook-behavior-on-supported-platforms)"
frozen-goal-revision: g-001
implementation-revision: "28251ea plus goal g-001 hook work"
status: partial
concrete-evidence-refs:
  - "cargo test --bin relay: 30 passed, 0 of 30 suite runs flaky after the test-root fix"
  - "python -m pytest tests/test_hook_increments.py: installed-path coverage passes"
  - "src/hook_runtime.rs: cfg(unix) permission-based injection is written but unevaluated on this Windows host"
required-test-refs:
  - T-HOOK-PLATFORM
classification-rationale: "Windows behavior, session isolation, installed-path coverage, and the removal of the magic retry count are proven. The Unix injection path and Unix parent-sync durability remain unevaluated here, so the requirement cannot be called satisfied."
```
