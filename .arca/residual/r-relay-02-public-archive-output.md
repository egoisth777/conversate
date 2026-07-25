# Residual record

```yaml
residual-id: r-relay-02-public-archive-output
goal-requirement-ref: "[REQ-002](../goal/spec.md#req-002--public-archive-output)"
frozen-goal-revision: g-001
implementation-revision: 28251ea
status: satisfied
concrete-evidence-refs:
  - tests/test_store_layout.py
  - tests/test_agent_facing_text_contract.py
  - tests/test_doctor_resolution_report.py
required-test-refs:
  - T-COMPAT
classification-rationale: Canonical `relay_archive` output and the deprecated `conversation_database` alias are asserted together across install, doctor, CLI, and agent-facing text suites, all green.
```
