# Ticket: t-06-fidelity-disposable-root-runner

```yaml
ticket-id: t-06-fidelity-disposable-root-runner
behavior-refs:
  - "[REQ-012](../../goal/spec.md#req-012--measured-context-fidelity-evidence)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-FIDELITY-RUN"
dependencies:
  - "t-05-fidelity-corpus"
status: done
```

## Scope

Build the disposable-root runner: populate a throwaway root from a record and its link closure, invoke the installed `relay context` binary, snapshot both roots, and record pack bytes, both token figures, budget outcome, latency, and any derived write observed inside the disposable root.

Reason: Measurement must never target the real archive, and the derived-write behavior itself is evidence.

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-FIDELITY-RUN-ISOLATION | REQ-012 | a source installation snapshot and a disposable root | `python -m pytest tests/test_context_fidelity_runner.py` | the source installation is byte-identical after every case including the minimum-minus-one error, and disposable-root derived writes are reported |
| T-FIDELITY-RUN-METRICS | REQ-012 | the five budget cases per record | `python -m pytest tests/test_context_fidelity_runner.py` | each case records pack bytes, independently computed ceil(bytes/4), Relay reported estimate, deviation, and latency |

## P5 proof and review

- Test result: python -m pytest tests/test_context_fidelity_runner.py: 10 passed against the built binary. Each case records pack bytes, ceil(bytes/4), Relay's root-normalized estimate, the deviation, latency, budget outcome, and derived writes.
- Review note: Measured on a disposable root only; the source installation stayed byte-identical in every case including the refused budget. Two behaviors were measured rather than assumed: a cold read published .semble/index-v2/* and index.jsonl, and the reported minimum budget was refused when offered back (for example 148 reported, 164 accepted). Mutation check: warming the root before the snapshot fails the cold-read test.
- Residual reverse reference: [r-relay-12-context-fidelity-evidence](../../residual/r-relay-12-context-fidelity-evidence.md)
