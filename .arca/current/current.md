phase: P5
status: running
current_revision: bootstrap
goal_revision: g-001
active_refs:
  - .arca/current/index.md
  - .arca/goal/index.md
  - .arca/residual/
  - .arca/ticket/
  - .arca/issue/archive/i-001-lossless-hook-increments/index.md
  - .arca/issue/archive/i-002-measured-context-fidelity/index.md
  - .arca/space/relay-sp/what/architecture.md
  - .arca/space/relay-sp/what/manifest.md
  - .arca/space/relay-sp/what/flows.md
waiting_on: none

Goal revision `g-001` is frozen. All nine tickets are implemented, proven, and archived. Residuals now read ten satisfied and three partial: REQ-011 because the Unix fault injection is unevaluated on this Windows host, REQ-012 because the corpus references no held-out real record and no provider is configured, and REQ-013 because five of its seven gates need receiver answers. No requirement is missing, but promotion is not due while any requirement is partial. The first fidelity baseline recorded two failing gates, five undecided gates, and three anomalies; per REQ-013 none of them was repaired here and each remedy needs its own P1 issue. `.arca/current/` remains delivered authority until promotion.
