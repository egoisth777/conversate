# conv save and park

Use this for `conv:save`, `conv:park`, auto-save reminders, and natural-language checkpoint requests.

## Steps

1. Ensure the store exists:
   `python .claude/skills/conv/scripts/conv_cli.py init`
2. Infer a concise topic and tags from the current conversation.
3. Extract state with this priority:
   - `dict`: terms coined or agreed on, with meanings. This is the highest-value section. Use `[[wikilinks]]` for terms that have graduated to `store/k/wiki/` concepts.
   - `sources`: files, skills, resources, and contexts used.
   - `qa`: sharp question/answer pairs; mark unresolved items as `**Q (open):**`.
   - `insights`: realizations worth preserving.
   - `decisions`: only settled decisions, with reasoning, and only if any exist.
4. Write JSON with `topic`, `status`, `tags`, optional `refs`, and `sections`.
5. Pipe it to:
   `python .claude/skills/conv/scripts/conv_cli.py upsert --stdin`
   Use `--status parked` for `conv:park`.
6. The CLI writes TOML markdown, reconciles reverse refs, and rebuilds `index.jsonl`.
7. For manual saves, present the inferred id/topic and invite rename. For auto-save, only print the one-line saved-as note.

## Extraction Template

Exclude acknowledgments, tool noise, and chatter. Write for a cold agent recovering headspace, not replaying a transcript.

```json
{
  "topic": "conversation database skill implementation",
  "status": "active",
  "tags": ["brain", "skill", "infra"],
  "refs": [],
  "sections": {
    "summary": "One line describing what this conversation is.",
    "dict": "- **term** - agreed meaning.",
    "qa": "- **Q:** question? **A:** answer.\n- **Q (open):** unresolved question?",
    "sources": "- file: path/to/file\n- skill: conv",
    "insights": "- Useful realization.",
    "decisions": "1. Decision and reasoning."
  }
}
```

Omit optional sections that have no substance. Do not omit `summary`, `dict`, or `qa`.
