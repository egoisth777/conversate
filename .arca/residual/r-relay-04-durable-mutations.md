# Residual record

```yaml
residual-id: r-relay-04-durable-mutations
goal-requirement-ref: "[REQ-004](../goal/spec.md#req-004--durable-mutations)"
frozen-goal-revision: g-001
implementation-revision: 28251ea
status: satisfied
concrete-evidence-refs:
  - tests/test_v2_io_contract.py
  - tests/test_index_cache.py
  - tests/test_branch_primitives.py
  - src/atomic_io.rs
  - cargo test: atomic_io::tests (3 passed)
required-test-refs:
  - T-FLOW
  - T-MAN
classification-rationale: Journal-before-replacement, ordered derived publication, and atomic replacement are covered by the v2 IO contract suite and the passing atomic_io Rust tests.
```
