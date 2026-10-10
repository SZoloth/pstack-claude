# pstack for Claude Code

A Claude Code port of [poteto's pstack](https://github.com/cursor/plugins/tree/main/pstack) (upstream 0.15.15, MIT). pstack is a set of rigorous agent workflows: `poteto-mode` routes a task to one of 23 playbooks (bug fix, feature, perf, refactor, babysit a PR, overnight runs), and runs review panels, parallel fan-outs, and 24 one-rule principle skills as the steps need them.

## Install

```bash
claude plugin marketplace add ~/Projects/pstack-claude
claude plugin install pstack@pstack-claude
```

Then, in a new session:

1. Run `/pstack:setup-pstack` to pick a budget and write `~/.claude/rules/pstack-models.md`. Optional: without it, every role uses its default.
2. Start rigorous work with `/pstack:poteto-mode <task and how to tell it's done>`.

Unsure which skill fits? `/pstack:poteto-help`.

## What changed from the Cursor original

| Cursor | This port |
|---|---|
| `Task` tool, any model slug | `Agent` tool with `fable`, `opus`, `sonnet`, `haiku`, or `inherit` |
| Grok as the second model family on review panels | Codex CLI (`codex exec`), wrapped by a cheap Sonnet agent. Falls back to Opus, with a warning, if Codex is not installed. |
| Grok for code delegates | Sonnet |
| Cloud agents | Background agents with `isolation: "worktree"` |
| `~/.cursor/rules/pstack-models.mdc` | `~/.claude/rules/pstack-models.md` |
| `/deslop`, `create-skill`, `control-ui`, `control-cli` | `/simplify`, `skill-creator`, the built-in browser tools, Bash plus tmux |
| Custom Modes (keep poteto-mode on every turn) | None. Invoke `/pstack:poteto-mode` per task. |
| `make-bot-ui` skill, benny automation pack | Dropped. Both depend on Cursor-hosted services. |

The full mapping that the skills read at run time is [`skills/poteto-mode/references/claude-code-runtime.md`](skills/poteto-mode/references/claude-code-runtime.md). The guide under `docs/guide/` is upstream's and still describes Cursor mechanics.

## Updating from upstream

```bash
port/sync.sh
```

It copies the latest upstream `skills/`, `agents/`, and `docs/` over this checkout, then runs `port/port.py` (context-free substitutions) and `port/hand_edits.py` (contextual edits that fail loudly when upstream text changed). It does not touch `setup-pstack/SKILL.md` or the runtime notes, which are written for this port. Review `git diff` before committing.
