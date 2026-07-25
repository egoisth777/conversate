# Residual record

```yaml
residual-id: r-relay-12-context-fidelity-evidence
goal-requirement-ref: "[REQ-012](../goal/spec.md#req-012--measured-context-fidelity-evidence)"
frozen-goal-revision: g-001
implementation-revision: 28251ea
status: partial
concrete-evidence-refs:
  - tools/fidelity/{corpus,runner,scoring,receiver,report,baseline}.py with tools/fidelity/corpus/corpus.json
  - "python -m pytest tests/test_context_fidelity_corpus.py: 12 passed"
  - "python -m pytest tests/test_context_fidelity_runner.py: 10 passed"
  - "python -m pytest tests/test_context_fidelity_scoring.py: 13 passed"
  - "python -m pytest tests/test_context_fidelity_receiver.py: 7 passed"
  - "python -m pytest tests/test_context_fidelity_baseline.py: 11 passed"
  - "baseline run over 7 synthetic records x 5 budgets: 35 cells, source installation unchanged, cold reads published .semble/index-v2/* and index.jsonl"
  - "corpus validation still reports: held-out records: 0 of 5 required"
required-test-refs:
  - T-FIDELITY-CORPUS
  - T-FIDELITY-RUN
classification-rationale: "The harness, corpus, disposable-root runner, scorer, receiver adapter, and report all exist and run, and every synthetic boundary case is measured with pack bytes, both token figures, the deviation, latency, and observed derived writes. Two inputs the requirement names are still absent. The corpus references no held-out real records because the archive holds one record, and no provider is configured, so measured provider input tokens and receiver answers stay unevaluated."
```
