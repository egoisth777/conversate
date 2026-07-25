# Residual record

```yaml
residual-id: r-relay-13-fidelity-decision-gate
goal-requirement-ref: "[REQ-013](../goal/spec.md#req-013--fidelity-decision-gate)"
frozen-goal-revision: g-001
implementation-revision: 28251ea
status: partial
concrete-evidence-refs:
  - tools/fidelity/report.py reports all seven named gates separately over the declared cells
  - "python -m pytest tests/test_context_fidelity_report.py: 11 passed"
  - "first baseline verdicts: source-recovery fail, robustness fail, critical-recall/continuation/provenance/safety/truncation-honesty insufficient-evidence"
  - "21 measured gaps and 14 anomalies recorded; product_change_authorized false"
required-test-refs:
  - T-FIDELITY-GATE
classification-rationale: The gate is computed rather than narrated, the worst cell decides, unevaluated cells block a pass, and efficiency numbers are descriptive and read by no gate. The gate cannot yet be decided because five of the seven gates need receiver answers that no configured provider produced, so the report states insufficient evidence instead of a verdict.
```
