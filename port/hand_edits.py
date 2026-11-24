#!/usr/bin/env python3
"""Contextual Cursor -> Claude Code edits. Run after port.py.

Usage: python3 port/hand_edits.py <plugin-root>

Each edit is (file, old, new). A missing `old` fails loudly, which is the
signal that upstream changed that passage and the edit needs a human look.
Edits already applied (new text present, old absent) are skipped. Removal
edits (empty `new`) always need `old`, so run this on fresh upstream copies
(port/sync.sh does).
"""
import pathlib
import sys

RT = "`poteto-mode/references/claude-code-runtime.md`"
SLUG_FALLBACK_OLD = "If the Agent tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message."
SLUG_FALLBACK_NEW = f"Valid values, and how to spawn a `codex` value, are under **Model values** in {RT}. If a value is invalid, use the default and say so."

EDITS = [
    # --- frontmatter ---
    ("skills/poteto-mode/SKILL.md", "name: Poteto Mode\n", "name: poteto-mode\n"),
    ("agents/comment-sicko.md", "name: Comment Sicko\n", "name: comment-sicko\n"),
    ("agents/comment-sicko.md",
     "description: A deranged comment-hater that savors deletion and condemns workaround code.\n",
     "description: A deranged comment-hater that savors deletion and condemns workaround code. Deletes comments only, never application code. Spawned by /pstack:no-comments.\n"),
    ("agents/poteto-agent.md", "is_background: true\n", "model: inherit\n"),
    ("agents/poteto-agent.md",
     "Read the `poteto-mode` skill's `SKILL.md` in full before doing any work, including its inline Principles index.",
     "Read the `poteto-mode` skill's `SKILL.md` in full before doing any work, including its inline Principles index. Your parent should pass the pstack plugin root. If it did not, get it from the `installPath` of the `pstack@...` entry in `~/.claude/plugins/installed_plugins.json`. Then read `skills/poteto-mode/SKILL.md` and `skills/poteto-mode/references/claude-code-runtime.md` under that root."),
    ("skills/poteto-mode/SKILL.md",
     "You own every subagent's work.",
     "Pass the absolute pstack plugin root (two levels above this skill's base directory) in every `pstack:poteto-agent` brief.\n\nYou own every subagent's work."),

    # --- poteto-mode: runtime pointer + Cursor-only routing ---
    ("skills/poteto-mode/SKILL.md", "# Poteto mode\n",
     f"# Poteto mode\n\n**Running in Claude Code.** Read {RT} once per session before your first spawn. It maps every Cursor mechanism below (Task, models, cloud agents, transcripts, control skills) onto Claude Code. Sibling pstack skills, including every `principle-*` leaf, live at `<this skill's base directory>/../<name>/SKILL.md`. Read them by path, because most of them block the Skill tool.\n"),
    ("skills/poteto-mode/SKILL.md",
     ", not Cursor's built-in babysit skill", ""),
    ("skills/poteto-mode/SKILL.md",
     "A line of `inherit-parent` or `auto` runs the role on the parent model, so omit `model` and spawn `general-purpose`, because `poteto-agent` defaults to Opus 5.5.",
     f"A line of `inherit` runs the role on the parent model. Resolve every role value per **Parsing a role value** in {RT}."),
    ("skills/poteto-mode/SKILL.md",
     "**Match the model to the job.** Start from the role's line or default, keep its family, and set the level the job needs. The `/setup-pstack` budget sets each role's starting level. Panel seats keep their listed level. Raise any other role one step, up to xhigh, for the hardest or subtlest work, lower it one step for judgment, and two or more steps for routine work. No role runs above xhigh. Opus 5.5 always runs its `-fast` slug. Verification always runs on the `swarm workers` model, `opus` by default. A Gemini seat runs at `codex` unless its line names another level. If the Agent tool rejects a slug, never pass it again. Fall back to the role's line or default, then the calling skill's fallback, then the closest valid slug of the same family, then omit `model`. Say so.",
     f"**Match the model to the job.** In Claude Code there are no speed or `-fast` slugs, so adjust only `effort`, and resolve values per **Parsing a role value** in {RT}. Start from the role's line or default, keep its family, and set the level the job needs. The `/setup-pstack` budget sets each role's starting level. Panel seats keep their listed level. Raise any other role one step, up to xhigh, for the hardest or subtlest work, lower it one step for judgment, and two or more steps for routine work. Verification always runs on the `swarm workers` model, `opus` by default. The cross-family panel seat runs via `codex` (see **Codex seats** in {RT}). If a value is invalid, fall back to the role's default and say so."),

    # --- cross-family panels: second seat is Codex ---
    ("skills/arena/SKILL.md",
     "An `auto` or `inherit-parent` entry is the parent model, so omit `model` and spawn `general-purpose`. If the Agent tool rejects a slug, use the nearest valid slug of the same family or drop the seat, keep at least two runners, and say so. Families go by prefix, and the longest match wins: `claude-fable-*`, `claude-*`, and `gemini-*`, after dropping a leading `cursor-`. Any other slug's family is its text before the first hyphen.",
     f"Resolve each entry per **Parsing a role value** in {RT}. Spawn a `codex` entry as a Codex seat per **Model values** in {RT}. A Codex runner is a writer, so it runs with the `workspace-write` sandbox in its own worktree. If an entry is invalid, run that seat on its family's default (`opus` for claude, `codex` for gpt) and say so. If a Codex seat is lost or Codex is not installed, drop the seat and say so."),
    ("skills/arena/SKILL.md",
     "After all Phase B candidates complete, spawn one readonly judge from the `arena cross-judge pool` line in `~/.claude/rules/pstack-models.md`, by default `opus`, `codex`. The judge is never from the parent's vendor, and Fable counts as Claude for that check, so use the first entry from another vendor. An `auto` or `inherit-parent` entry is the parent model. If you do not know the parent's model, use the first real slug and say that the vendor check did not run. If the Agent tool rejects a slug, use the nearest valid slug of the same family, then the next such entry, or skip the judge, and say so.",
     f"After all Phase B candidates complete, spawn one read-only judge (or a read-only Codex seat when the entry is `codex`, see **Model values** in {RT}) from the `arena cross-judge pool` line in `~/.claude/rules/pstack-models.md`, by default `opus`, `codex`. The judge is never from the parent's vendor, and Fable counts as Claude for that check, so a Claude parent uses `codex`. Resolve each entry per **Parsing a role value** in {RT}. If the entry is unavailable, fall back to the next entry or skip the judge and say so."),

    # --- swarm ---
    ("skills/swarm/SKILL.md", SLUG_FALLBACK_OLD, SLUG_FALLBACK_NEW),
    ("skills/swarm/SKILL.md", "Use `environment: \"local\"` only when the worker needs access to something on the user's computer.",
     "Drop `isolation` for a read-only worker that writes nothing. Use `isolation: \"remote\"` only when the session offers it and the worker needs nothing on this machine. Run at most about 6 workers at once on one machine and queue the rest."),
    ("skills/swarm/SKILL.md", "When a worker must start from a non-default pushed branch, pass `cloud_base_branch`.",
     "When a worker must start from a non-default pushed branch, its brief's first step is `git fetch origin <branch> && git switch -C <worker-branch> origin/<branch>` in its worktree."),

    # --- automate-me ---
    ("skills/automate-me/SKILL.md",
     "Shape: one or two questions with 4-6 options each, `allow_multiple: true` for category questions.",
     "Shape: one or two questions with 2-4 options each (the tool's limit; it adds an \"Other\" option itself), `multiSelect: true` for category questions."),

    # --- recall: transcripts ---
    ("skills/recall/SKILL.md",
     "Transcripts live at `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`, where `<slug>` is the workspace path with the leading slash dropped and each \"/\" turned into \"-\" (so `/Users/you/proj` becomes `Users-you-proj`).",
     "Transcripts live at `~/.claude/projects/<slug>/<session-id>.jsonl`, where `<slug>` is the working directory with every \"/\" and \".\" turned into \"-\" (so `/Users/you/proj` becomes `-Users-you-proj`)."),

    # --- playbooks: cloud agents, Cursor features ---
    ("skills/poteto-mode/playbooks/shipping.md", "each a Cursor cloud agent,", "each a background agent in its own worktree,"),
    ("skills/poteto-mode/playbooks/autopilot-full.md", "Each owner is a Cursor cloud agent that builds", "Each owner is a background agent, in its own worktree, that builds"),
    ("skills/poteto-mode/playbooks/worktree-cleanup.md", "lives at `.cursor/worktrees/myrepo/x`", "lives at `.claude/worktrees/x`"),
    ("skills/poteto-mode/playbooks/worktree-cleanup.md",
     "`~/Library/Application Support/Cursor` (`state.vscdb.backup`, and `snapshots/roots/<root>` where a `<root>` named for a folder you opened as a workspace balloons),",
     "`~/.claude/projects/` (session transcripts, which are history, so ask before deleting any),"),

    ("skills/poteto-mode/scripts/worktree-audit.sh",
     "# Transcripts dir: ~/.cursor/projects/<slugified-repo-path>/agent-transcripts.",
     "# Transcripts dir: ~/.claude/projects/<repo path with / and . turned into ->."),
    ("skills/poteto-mode/scripts/worktree-audit.sh",
     "slug=$(printf '%s' \"$main_wt\" | sed 's#^/##; s#/#-#g')",
     "slug=$(printf '%s' \"$main_wt\" | sed 's#[/.]#-#g')"),
    ("skills/poteto-mode/scripts/worktree-audit.sh",
     'transcripts="$HOME/.cursor/projects/$slug/agent-transcripts"',
     'transcripts="$HOME/.claude/projects/$slug"'),

    ("docs/guide/README.md", "# The pstack guide\n",
     "> Written for the Cursor original. For Claude Code mechanics (models, subagents, transcripts, control tools), see [the runtime notes](../../skills/poteto-mode/references/claude-code-runtime.md).\n\n# The pstack guide\n"),

    # --- poteto-help ---
    ("skills/poteto-help/SKILL.md", "and mention once that a Custom Mode keeps it on.", "and mention once that `/pstack:poteto-mode` applies per task."),
    ("skills/poteto-help/SKILL.md",
     "The links here point into the installed plugin, which the user may not be able to open, so give the user the file's public copy: `https://github.com/cursor/plugins/blob/main/pstack/` followed by its path.",
     "The links here point into the installed plugin. Give the user the absolute path under the plugin root. The upstream Cursor original is at `https://github.com/cursor/plugins/blob/main/pstack/` followed by the same path."),
    ("skills/poteto-help/SKILL.md", "1. Install with `/add-plugin pstack` in chat, or from Customize in the sidebar.",
     "1. Install with `/plugin install pstack@pstack-claude` after adding the marketplace (see the README)."),
    ("skills/poteto-help/SKILL.md", "The rule applies to new chats.", "The rule loads in new sessions."),
    ("skills/poteto-help/SKILL.md",
     "A role set to `auto` or `inherit-parent` runs on the chat's model, which saves tokens when the chat runs on Auto or a cheaper model.",
     "A role set to `inherit` runs on the session's model. Setting the panel's `codex` seat spends Codex quota instead of Claude tokens."),
    ("skills/poteto-help/SKILL.md",
     "pstack is built for Cursor, and it also installs in Claude Code with `/plugin marketplace add cursor/plugins`, then `/plugin install pstack@cursor-plugins`. There, each command takes a `pstack:` prefix, such as `/pstack:poteto-mode`. The [Claude Code adapter](../../docs/harness/claude-code.md) maps the Cursor names, and a step that needs a Cursor-only feature, such as Bugbot or Automations, is skipped with a one-line note.\n\nOther tools can read the skills, because they use the Agent Skills format. But most workflow skills, including `/poteto-mode`, `/how`, and `/teach`, spawn Cursor subagents, some with per-role models, and Custom Modes and `/loop` are Cursor features, so those parts may not work there.",
     f"This is a Claude Code port of a Cursor plugin. Each command takes a `pstack:` prefix, such as `/pstack:poteto-mode`. [The runtime notes](../poteto-mode/references/claude-code-runtime.md) map the Cursor mechanisms onto Claude Code, and a step that needs a Cursor-only feature, such as Bugbot or Automations, is skipped with a one-line note. Cross-family review seats run through the Codex CLI."),
    ("docs/harness/claude-code.md", "# pstack in Claude Code\n",
     "> This is the upstream adapter. This port ships its own mapping in [the runtime notes](../../skills/poteto-mode/references/claude-code-runtime.md), which wins wherever the two disagree (for example `run_in_background`, `resume`, `codex` model values, and Codex seats).\n\n# pstack in Claude Code\n"),
    ("skills/poteto-help/SKILL.md",
     "- Enter on `/poteto-mode` attaches the skill to one message. It fades as the chat moves on.\n- Option+Enter on Mac or Alt+Enter on Windows, or Use as Mode from the skill entry, makes it a Custom Mode. It stays in context every turn until the user exits the mode, and it stays out of casual turns.\n- Cursor's docs list Custom Modes in the Agents Window and the CLI. Elsewhere, start each new task with `/poteto-mode`.\n\nLink [Cursor's skills docs](https://cursor.com/docs/skills) when this comes up.",
     "- `/pstack:poteto-mode` loads the skill into the session. It fades as the chat moves on and context compacts.\n- Claude Code has no Custom Modes, so start each new task with `/pstack:poteto-mode`."),
    ("skills/poteto-help/SKILL.md", "| Run parallel checks over slices, or race workers, as cloud agents |", "| Run parallel checks over slices, or race workers, as isolated background agents |"),
    ("skills/poteto-help/SKILL.md",
     "- `/simplify`, `control-cli`, and `control-ui` ship in the `cursor-team-kit` plugin.\n- `/loop` and `/skill-creator` are Cursor built-ins.",
     f"- `/simplify` and `/loop` are Claude Code built-ins. `skill-creator` is Anthropic's skill-authoring skill.\n- `control-cli` and `control-ui` are roles, not skills. {RT} names the Claude Code tools that fill them."),
    ("skills/poteto-help/SKILL.md", "Without `/poteto-mode`, a phrase such as \"babysit this pr\" can start Cursor's own skill for the same job instead. ", ""),
    ("skills/poteto-help/SKILL.md", "| It was started with Enter. Start it as a Custom Mode, or start each task with `/poteto-mode`. |",
     "| Context compacted or the task changed. Start each task with `/pstack:poteto-mode`. |"),
    ("skills/poteto-help/SKILL.md", "The rule from `/setup-pstack` applies to new chats. Start one.", "The rule from `/setup-pstack` loads at session start. Start a new session."),
    ("skills/poteto-help/SKILL.md", "or run them as cloud agents, which each get their own machine.", "by spawning them with `isolation: \"worktree\"`."),
]


def main() -> None:
    root = pathlib.Path(sys.argv[1])
    failed = []
    for rel, old, new in EDITS:
        path = root / rel
        text = path.read_text()
        if new and new in text:
            continue
        if old in text:
            path.write_text(text.replace(old, new, 1))
        else:
            failed.append((rel, old[:90]))
    for rel, old in failed:
        print(f"MISSING in {rel}: {old!r}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
