+++
id = "fx-malformed-link"
topic = "Malformed link value"
status = "active"
refs = [{ id = "   ", rel = "informed-by" }]
relay_schema = 2
created = 2026-01-01T00:00:00Z
updated = 2026-01-01T00:00:00Z
+++
## summary
Reference values are malformed.

## glossary
- **malformed reference** - a link value that is not a usable record id.

## qa
- **Q:** Must a malformed link abort the pack? **A:** It must be reported, not silently dropped.
