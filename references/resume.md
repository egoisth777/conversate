# conv resume

Use this for `conv:resume` and natural-language requests to resume or continue a previous discussion.

## Resolve Target

1. Run:
   `python .claude/skills/conv/scripts/conv_cli.py search "<user query>"`
2. If exactly one confident hit returns, use it.
3. If multiple hits return, present the ranked ids/topics and ask the user to choose.
4. Show the resolved conversation:
   `python .claude/skills/conv/scripts/conv_cli.py show <id> --markdown`

The CLI implements the tiered cascade as filename/path match, `rg` over `index.jsonl`, then Semble over `conv/log` bodies. It uses installed `semble` automatically, can use `uvx semble` when `CONV_USE_UVX_SEMBLE=1`, and otherwise falls back to built-in body scoring. If `fff` is available, prefer it manually for the filename layer; keep the same short-circuit behavior.

## Reconstruction Order

Read and internalize in this order:

1. Frontmatter: identity, status, tags, refs.
2. `## summary`: orientation.
3. `## dict`: ubiquitous language first.
4. `## qa`: spine of the conversation; treat `Q (open)` entries as live threads.
5. `## sources`: read listed files and invoke listed skills only when needed for the resumed task.
6. `## insights`: useful realizations.
7. `## decisions`: settled items. Do not relitigate them unless the user asks.
8. Linked conversations through frontmatter refs. Surface useful branch digests from closed peers.

After loading, mark the conversation active:

`python .claude/skills/conv/scripts/conv_cli.py set-status <id> active`

Then present a short summary and open threads.
