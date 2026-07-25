# Issue ubiquitous language

These terms are local to the measured context-fidelity issue.

| Term | Meaning |
| :--- | :--- |
| **baseline harness** | A reproducible runner that invokes the installed production `relay context` path against a disposable Relay root, leaves the source installation unchanged, and records any derived state the production path writes inside that disposable root. |
| **gold fact** | An exact path, command, ID, version, constraint, decision, test result, or pending-work item enumerated from the source evidence before a context pack is evaluated. |
| **disposable Relay root** | A throwaway installation root populated from the evaluated record and its link closure, used so that measurement never targets the source archive. |
| **decisive gate** | A gate whose result drives the stop-or-escalate decision: critical recall, continuation, provenance, safety, truncation honesty, source recovery, and robustness. |
| **compression efficiency** | The measured provider input tokens, pack bytes, and elapsed time required to recover gold facts and complete the scripted next task; raw text reduction alone is insufficient. |
| **context recovery rate** | The exact-match percentage of gold facts recovered by a fresh session, reported by fact kind and paired with the scripted continuation result. |
| **capture loss** | A gold fact that was available in the source evidence but never entered the durable Relay record. |
| **trim loss** | A gold fact present in the durable Relay record but omitted from the emitted context pack. |
| **fresh-session continuation** | A new receiver session is given one context pack and one scripted next task without access to the source record unless the pack directs a bounded recovery action. |
| **equal end-to-end cost** | A comparison that includes compressor and receiver tokens, bytes, retries, latency, and required human intervention. |
| **held-out record** | A real Relay record excluded from harness construction and used only for evaluation. |
