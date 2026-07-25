# Residual record

```yaml
residual-id: r-relay-01-archive-authority
goal-requirement-ref: "[REQ-001](../goal/spec.md#req-001--archive-authority)"
frozen-goal-revision: g-001
implementation-revision: 28251ea
status: satisfied
concrete-evidence-refs:
  - "tests/test_store_layout.py"
  - "tests/test_index_cache.py"
  - "python -m pytest: 283 passed, 24 subtests passed"
required-test-refs:
  - "T-ARCH"
  - "T-VERIFY"
classification-rationale: "Store-layout and index-cache suites exercise the archive as source of truth and rebuild derived state from it; the full Python suite passed at implementation revision 28251ea."
```
