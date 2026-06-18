# conv list

Use this for `conv:list`, "what's open", and recent conversation requests.

## Commands

- Active, parked, then recent closed:
  `python .claude/skills/conv/scripts/conv_cli.py list --limit 10`
- JSON for further filtering:
  `python .claude/skills/conv/scripts/conv_cli.py list --json --limit 50`
- Filter one status:
  `python .claude/skills/conv/scripts/conv_cli.py list --status active --limit 20`

The list command reads only `index.jsonl`. It does not read conversation markdown files. The `open` column is a derived cache count rebuilt from `## qa` whenever the index is rebuilt.
