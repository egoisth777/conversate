+++
id = "fx-mixed-weights"
topic = "Mixed transcript weights"
status = "active"
refs = []
relay_schema = 2
created = 2026-01-01T00:00:00Z
updated = 2026-01-01T00:00:00Z
+++
## summary
Weighted transcript trimming fixture.

## glossary
- **weight** - durable 1-3 importance on a condensed exchange.

## qa
- **Q:** Which command must run before every handoff? **A:** cargo test
- **Q:** Which file holds the counter? **A:** src/hook_runtime.rs

## transcript
- **Q:** Should the aside survive trimming? **A:** No, the low-weight aside may go first.
