# Residual record

```yaml
residual-id: r-relay-08-read-only-legacy-import
goal-requirement-ref: "[REQ-008](../goal/spec.md#req-008--read-only-legacy-import)"
frozen-goal-revision: g-001
implementation-revision: 28251ea
status: satisfied
concrete-evidence-refs:
  - tests/test_install.py
  - tests/test_store_layout.py
required-test-refs:
  - T-ARCH
classification-rationale: Legacy `~/.conversate/` handling, collision reporting, and source immutability are asserted by the install and store-layout suites, which passed.
```
