+++
id = "fx-missing-link"
topic = "Missing link target"
status = "active"
refs = [{ id = "fx-does-not-exist", rel = "informed-by" }]
relay_schema = 2
created = 2026-01-01T00:00:00Z
updated = 2026-01-01T00:00:00Z
+++
## summary
The referenced record is absent from the archive.

## glossary
- **dangling reference** - a link whose target cannot be resolved.

## qa
- **Q:** What must the pack do with an unresolved link? **A:** It must report the unresolved link.
