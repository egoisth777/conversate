# Ticket: t-05-fidelity-corpus

```yaml
ticket-id: t-05-fidelity-corpus
behavior-refs:
  - "[REQ-012](../../goal/spec.md#req-012--measured-context-fidelity-evidence)"
design-refs:
  - "[Target mechanics](../../goal/design.md#target-mechanics)"
planned-test-refs:
  - "T-FIDELITY-CORPUS"
dependencies:
  - "none"
status: done
```

## Scope

Define and validate the versioned fidelity corpus: held-out real record references, synthetic boundary fixtures, gold facts, scripted continuation tasks, budgets, receivers, and redaction rules.

Reason: Every later measurement depends on a corpus that is reproducible and free of private content.

## P4 test plan

| Planned test ID | Goal contract ref | Fixture/ref setup | Executable target | Observable oracle |
| :--- | :--- | :--- | :--- | :--- |
| T-FIDELITY-CORPUS-SHAPE | REQ-012 | a corpus manifest with real references and synthetic fixtures | `python -m pytest tests/test_context_fidelity_corpus.py` | the manifest validates, resolves at least five held-out records, covers every required boundary case, and contains no private body or secret |

## P5 proof and review

- Test result: python -m pytest tests/test_context_fidelity_corpus.py: 12 passed. Corpus manifest tools/fidelity/corpus/corpus.json with 7 synthetic boundary fixtures, gold facts quoted from their fixtures, 5 budget cases, and declared known_gaps.
- Review note: Validation reports problems instead of raising, so the missing held-out real records stay visible as `held-out records: 0 of 5 required`. Mutation check: a validator that always returns a clean list fails 8 of 11 checks. Held-out real records are still absent because the archive holds one record; REQ-012 stays partial for that reason.
- Residual reverse reference: [r-relay-12-context-fidelity-evidence](../../residual/r-relay-12-context-fidelity-evidence.md)
