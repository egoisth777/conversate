---
name: conv
description: Persist, retrieve, list, park, branch, return, continue, and repair topic-bound conversations in the brain/conv store. Use for explicit commands like conv:save, conv:resume, conv:list, conv:park, conv:sidekick, conv:return, conv:continue, conv:regen; natural language such as save this, checkpoint this, resume the auth discussion, what conversations are open, sidekick this, bring the branch back, or continue fresh; and UserPromptSubmit auto-save reminders.
---

# conv

Use this skill to manage the conversation database in `conv/`.

## Invariants

- Treat `conv/log/*.md` as source of truth. Treat `conv/index.jsonl` as a derived cache.
- Use TOML frontmatter delimited by `+++`; do not touch the YAML vault outside `conv/`.
- Every conversation must have a topic and the mandatory body sections `## summary`, `## dict`, and `## qa`.
- Reconstruct language first: read `## dict` before `## qa`, sources, insights, or decisions.
- Keep frontmatter thin: id, topic, status, tags, refs, created, updated.
- Keep refs bidirectional with valued directional labels:
  - `spawned-from` <-> `spawned-to`
  - `continued-from` <-> `continued-as`
  - `informed-by` <-> `informed`
- Never mutate `## decisions` unless the user explicitly asks to edit decisions. Contradictions from branches go into `## qa` as open questions.
- Use the CLI for writes, index rebuilds, status changes, and ref regeneration:
  `python .claude/skills/conv/scripts/conv_cli.py <command>`.

## Routing

- For `conv:save`, auto-save reminders, "save this", or "checkpoint this", read `references/save.md`.
- For `conv:resume` or "continue where we left off", read `references/resume.md`.
- For `conv:list`, "what's open", or recent/open conversation lists, read `references/list.md`.
- For `conv:park`, read `references/save.md` and save with status `parked`.
- For `conv:sidekick`, `conv:return`, or `conv:continue`, read `references/branching.md`.
- For `conv:regen`, drift checks, CLI details, or implementation troubleshooting, read `references/cli.md`.

## Auto-Save Behavior

When a hook injects `CONV AUTO-SAVE: threshold reached`, immediately run the `conv:save` flow silently. Infer the id and topic, write the checkpoint, rebuild the index, and tell the user only:

`Auto-saved as <id> - rename anytime.`

Do not block the user's current task for confirmation.
