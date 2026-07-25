# Residual record

```yaml
residual-id: r-relay-10-hook-counter-outcomes
goal-requirement-ref: "[REQ-010](../goal/spec.md#req-010--explicit-hook-counter-outcomes)"
frozen-goal-revision: g-001
implementation-revision: "28251ea plus goal g-001 hook work"
status: satisfied
concrete-evidence-refs:
  - "cargo test --bin relay: absent, existing, malformed, unreadable, saturated, and blocked-replacement cases pass"
  - "src/atomic_io.rs write_atomic_staged reports Prepare, Replace, or ParentSync"
  - "mutation check: swallowing a staged write failure fails blocked_replacement_preserves_published_counter"
required-test-refs:
  - T-HOOK-OUTCOMES
classification-rationale: "Outcomes are classified, a blocked replacement leaves the published counter intact, and unparseable content is quarantined as evidence before the count restarts. ParentSync uncertainty is proven only through its mapping function because Windows sync_parent is a documented no-op."
```
