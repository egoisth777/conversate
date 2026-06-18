# conv CLI

The shared helper is:

`python .claude/skills/conv/scripts/conv_cli.py <command>`

## Commands

- `init`: create `conv/`, `conv/log/`, `conv/.semble/`, and rebuild `index.jsonl`.
- `upsert --stdin`: create or replace a conversation from JSON.
- `rebuild-index`: rebuild `index.jsonl` from `conv/log/*.md`.
- `regen-refs`: repair missing reverse refs, then rebuild the index.
- `list [--status active|parked|closed] [--json] [--limit N]`: index-only listing.
- `search "<query>" [--limit N]`: tiered filename/index/body search.
- `show <id-or-query> [--markdown]`: print one conversation.
- `set-status <id> active|parked|closed`: update status and timestamp.
- `doctor`: validate layout, optional tools, parseability, and index count.

## Turn Counter Shim

`.claude/hooks/conv-turn-counter.ps1` is the current session-scoped turn counter. It writes `$env:TEMP/conv-session-<PID>.count` and emits the auto-save reminder once the count is greater than 10. Keep this hook single-purpose: future zig/rust daemon work may replace the temp-file backend, but index rebuilds and ref regeneration remain persistent CLI responsibilities.

There is no timer for ref regeneration. `upsert` runs the eager write plus a byte-stable regen sweep, and `regen-refs` is the manual full reconciliation command.

The semantic search layer runs `semble search -k <N> <query> conv/log --content docs` when `semble` is installed. To allow transient `uvx semble`, set `CONV_USE_UVX_SEMBLE=1`; it is opt-in because first-run indexing can be slow. If neither path is available, the CLI falls back to local body scoring and labels those hits `semble-body-fallback`.

## JSON Shape for upsert

```json
{
  "id": "conv_260616_optional-slug",
  "topic": "required topic",
  "status": "active",
  "tags": ["optional"],
  "refs": [{"id": "conv_260615_parent", "rel": "spawned-from"}],
  "sections": {
    "summary": "required",
    "dict": "- **term** - meaning",
    "qa": "- **Q:** question? **A:** answer."
  }
}
```

If `id` is omitted, the CLI generates `conv_<YYMMDD>_<topic-slug>` and writes `conv/log/<YYYY-MM-DD>_<topic-slug>.md`.

`summary`, `dict`, and `qa` are mandatory. Optional sections are omitted when empty.
