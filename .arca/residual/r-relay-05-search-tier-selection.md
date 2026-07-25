# Residual record

```yaml
residual-id: r-relay-05-search-tier-selection
goal-requirement-ref: "[REQ-005](../goal/spec.md#req-005--search-tier-selection)"
frozen-goal-revision: g-001
implementation-revision: 28251ea
status: satisfied
concrete-evidence-refs:
  - tests/test_search_tiers.py
  - tests/test_doctor_resolution_report.py
  - cargo test: search_backend::tests (8 passed)
required-test-refs:
  - T-FLOW
classification-rationale: Tier selection, the `RELAY_USE_UVX_SEMBLE=1` opt-in, fallback scoring, and doctor agreement are asserted in Python and Rust; all cited tests passed.
```
