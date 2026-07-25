# Ticket: t-08-fidelity-receiver-adapter

```yaml
ticket-id: t-08-fidelity-receiver-adapter
behavior-refs:
  - "[REQ-012](../../goal/spec.md#req-012--measured-context-fidelity-evidence)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-FIDELITY-RUN"
dependencies:
  - "t-06-fidelity-disposable-root-runner"
status: done
```

## Scope

Add the configured receiver adapter that hands a pack to a fresh session on at least two providers, runs the scripted continuation task against a raw-context baseline, and records provider telemetry without credentials in the repository.

Reason: Provider evidence is required for the full report but must not make ordinary local runs need network access.

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-FIDELITY-RECEIVER-OPTIONAL | REQ-012 | no configured provider credentials | `python -m pytest tests/test_context_fidelity_receiver.py` | local runs pass with every provider case explicitly unevaluated, never counted as a pass |
| T-FIDELITY-RECEIVER-TELEMETRY | REQ-012 | a stubbed receiver transport | `python -m pytest tests/test_context_fidelity_receiver.py` | provider, model, host, input tokens, retries, and intervention are recorded in redacted form |

## P5 proof and review

- Test result: python -m pytest tests/test_context_fidelity_receiver.py: 7 passed with no network access and no credentials in the repository.
- Review note: Without a credential every provider cell is `unevaluated` and never a pass; an exhausted transport stays unevaluated too. Telemetry records provider, model, host, input tokens, retries, and intervention, and the credential value is redacted from every recorded field. The raw-record baseline runs beside the pack for the same scripted task.
- Residual reverse reference: [r-relay-12-context-fidelity-evidence](../../residual/r-relay-12-context-fidelity-evidence.md)
