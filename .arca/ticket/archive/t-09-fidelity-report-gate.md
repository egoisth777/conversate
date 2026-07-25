# Ticket: t-09-fidelity-report-gate

```yaml
ticket-id: t-09-fidelity-report-gate
behavior-refs:
  - "[REQ-013](../../goal/spec.md#req-013--fidelity-decision-gate)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-FIDELITY-GATE"
dependencies:
  - "t-07-fidelity-scorer"
  - "t-08-fidelity-receiver-adapter"
status: done
```

## Scope

Generate the versioned fidelity report and evaluate the decision gate: per-gate pass or fail over the declared decision set, worst-case reporting, descriptive efficiency numbers, and no product change.

Reason: The gate exists to stop unjustified feature work, so it must be computed, not narrated.

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-FIDELITY-GATE-REPORT | REQ-013 | scored cases across several matrix cells | `python -m pytest tests/test_context_fidelity_report.py` | each decisive gate is reported separately, the worst cell decides, and unevaluated cells stay visible |
| T-FIDELITY-GATE-NO-CHANGE | REQ-013 | a failing gate result | `python -m pytest tests/test_context_fidelity_report.py` | the report records the measured gap and the run changes no product output, schema, or record |

## P5 proof and review

- Test result: python -m pytest tests/test_context_fidelity_report.py: 11 passed; python -m pytest tests/test_context_fidelity_baseline.py: 11 passed. First baseline over the shipped corpus: source-recovery fail, robustness fail, and critical-recall, continuation, provenance, safety, truncation-honesty all insufficient-evidence; 21 measured gaps and 14 anomalies recorded.
- Review note: All seven gates named by REQ-013 are reported separately, the worst cell decides, unevaluated cells block a pass instead of being ignored, and efficiency is printed as a descriptive yardstick that no gate reads. The run authorized no product change. Mutation checks: letting unevaluated cells pass fails one check; claiming efficiency is graded fails another.
- Residual reverse reference: [r-relay-13-fidelity-decision-gate](../../residual/r-relay-13-fidelity-decision-gate.md)
