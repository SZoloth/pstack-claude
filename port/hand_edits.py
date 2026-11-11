#!/usr/bin/env python3
"""Contextual Cursor -> Claude Code edits. Run after port.py.

Usage: python3 port/hand_edits.py <plugin-root>

Each edit is (file, old, new). A missing `old` fails loudly, which is the
signal that upstream changed that passage and the edit needs a human look.
Edits already applied (new text present, old absent) are skipped.
"""
import pathlib
import sys

RT = "`poteto-mode/references/claude-code-runtime.md`"
SLUG_FALLBACK_OLD = "If the Agent tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message."
SLUG_FALLBACK_NEW = f"Valid values, and how to spawn a `codex` value, are under **Model values** in {RT}. If a value is invalid, use the default and say so."

EDITS = [
    # --- frontmatter ---
    ("skills/poteto-mode/SKILL.md", "name: Poteto Mode\n", "name: poteto-mode\n"),
    ("skills/poteto-mode/SKILL.md",
     "mode: true\nicon: crown\ncolor: yellow\nreminder: New task? Playbook match or rigor needed -> apply /poteto-mode. Casual turn or user opts out -> don't.\n", ""),
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
     "`cursor-team-kit` publishes `control-cli` (CLIs and TUIs) and `control-ui` (browser / Electron / web UIs).",
     f"`control-cli` covers CLIs and TUIs. `control-ui` covers browser, Electron, and web UIs. **Control skills** in {RT} names the Claude Code tools for each."),
    ("skills/poteto-mode/SKILL.md",
     ", not Cursor's built-in babysit skill, whose description matches the same words", ""),
    ("skills/poteto-mode/SKILL.md", "agent mode (readonly strips MCP), ", ""),
    ("skills/poteto-mode/SKILL.md",
     "Defaults `sonnet` for code, `opus` for prose and judgment). Code delegates",
     "Defaults `sonnet` for code, `opus` for prose and judgment, and `codex` for the cross-family seat on panels). Code delegates"),
    ("skills/poteto-mode/SKILL.md",
     "a role line of `inherit-parent` or `auto` runs that role on the parent chat model (omit Task `model`)",
     "a role line of `inherit` runs that role on the parent chat model. Resolve every role value per **Parsing a role value** in `poteto-mode/references/claude-code-runtime.md`"),
    ("skills/poteto-mode/SKILL.md", "from a transcript, cloud-agent URL, or pushed branch",
     "from a transcript, remote session, or pushed branch"),

    # --- shared role-line boilerplate ---
    ("skills/how/SKILL.md", SLUG_FALLBACK_OLD, SLUG_FALLBACK_NEW),
    ("skills/why/SKILL.md", SLUG_FALLBACK_OLD, SLUG_FALLBACK_NEW),
    ("skills/reflect/SKILL.md", SLUG_FALLBACK_OLD, SLUG_FALLBACK_NEW),

    # --- cross-family panels: second seat is Codex ---
    ("skills/arena/SKILL.md",
     "default to one each on `opus` and `sonnet`.",
     "default to one each on `opus` and `codex`."),
    ("skills/arena/SKILL.md",
     "An `auto` or `inherit-parent` entry in this line means the parent model, so omit `model` for it. If the Agent tool rejects a configured entry, run that seat on its family's default and say so. Families go by prefix: `claude-*`, and `grok-*` with `cursor-grok-*` and `composer-*`. A refused `composer-*` entry runs on `sonnet`. If the family has no default, or the Agent tool rejects that default, use the closest valid slug of the same family from its error message, or drop the seat and say so when there is none.",
     f"Resolve each entry per **Parsing a role value** in {RT}. Spawn a `codex` entry as a Codex seat per **Model values** in {RT}. A Codex runner is a writer, so it runs with the `workspace-write` sandbox in its own worktree. If an entry is invalid, run that seat on its family's default (`opus` for claude, `codex` for gpt) and say so. If a Codex seat is lost or Codex is not installed, drop the seat and say so."),
    ("skills/arena/SKILL.md", "choose from `opus` and `sonnet`.", "choose from `opus` and `codex`."),
    ("skills/arena/SKILL.md", "Spawn one readonly judge subagent.",
     f"Spawn one read-only judge subagent, or a read-only Codex seat when the entry is `codex` (see **Model values** in {RT})."),
    ("skills/arena/SKILL.md", "With the default pool, a Claude parent gets `sonnet`.", "With the default pool, a Claude parent gets `codex`."),
    ("skills/architect/SKILL.md", "use `opus` and `sonnet`.", "use `opus` and `codex`."),

    # --- swarm ---
    ("skills/swarm/SKILL.md", SLUG_FALLBACK_OLD, SLUG_FALLBACK_NEW),
    ("skills/swarm/SKILL.md", "Use `environment: \"local\"` only when the worker needs access to something on the user's computer.",
     "Drop `isolation` for a read-only worker that writes nothing. Use `isolation: \"remote\"` only when the session offers it and the worker needs nothing on this machine. Run at most about 6 workers at once on one machine and queue the rest."),
    ("skills/swarm/SKILL.md", "When a worker must start from a non-default pushed branch, pass `cloud_base_branch`.",
     "When a worker must start from a non-default pushed branch, its brief's first step is `git fetch origin <branch> && git switch -C <worker-branch> origin/<branch>` in its worktree."),
    ("skills/reflect/SKILL.md",
     "in the `agent-transcripts/` directory the system prompt names.",
     "per **Transcripts** in `poteto-mode/references/claude-code-runtime.md`."),
    ("skills/reflect/SKILL.md",
     "That covers the legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent (`<parent>/subagents/<child>.jsonl`) layouts. For each candidate, read the first JSONL line. Take the file whose `message.content[0].text` contains the conversation's opening user prompt.",
     "That covers the session files and the subagent transcripts (`<session-id>/subagents/<child>.jsonl`). For each candidate, find the first record with `\"type\":\"user\"` (see **Transcripts** in `poteto-mode/references/claude-code-runtime.md`). Take the file where it contains the conversation's opening user prompt."),
    ("skills/automate-me/SKILL.md",
     "Shape: one or two questions with 4-6 options each, `allow_multiple: true` for category questions.",
     "Shape: one or two questions with 2-4 options each (the tool's limit; it adds an \"Other\" option itself), `multiSelect: true` for category questions."),
    ("skills/poteto-mode/playbooks/multi-phase-plan.md",
     "Run `node pstack/skills/poteto-mode/scripts/check-plan.mjs <plan.md>`",
     "Run `node <pstack-root>/skills/poteto-mode/scripts/check-plan.mjs <plan.md>` (`<pstack-root>` per **Finding pstack files** in `poteto-mode/references/claude-code-runtime.md`)"),

    # --- why: MCP discovery ---
    ("skills/why/SKILL.md",
     "list the available MCPs from the Cursor environment. Use the available-tools map when present. Otherwise inspect the `mcps/` directory Cursor exposes for enabled MCP servers.",
     "list the MCP servers available in this Claude Code session: tools named `mcp__<server>__*`, plus deferred tools you can surface with `ToolSearch`. A CLI on `PATH` (such as `gh`, `linear`, or `sentry-cli`) counts as a source too."),

    # --- Cursor-only mechanics that would mislead an agent ---
    ("skills/why/SKILL.md",
     "Every spawn is `general-purpose` with `readonly: false` (agent mode). **Do not use readonly/Ask mode.** It strips MCP access, which disables the MCP-backed investigators and the synthesizer's citation spot-checks. Investigators still shouldn't write anything.",
     "Every spawn is `general-purpose`, which keeps the session's MCP servers. Say \"read-only: do not edit or write files\" in each brief, because investigators still shouldn't write anything."),
    ("skills/poteto-mode/SKILL.md",
     "**Match the model to the job.** Before each spawn,",
     f"**Match the model to the job.** In Claude Code there are no speed or `-fast` slugs, so adjust only `effort`, and resolve values per **Parsing a role value** in {RT}. Before each spawn,"),
    ("skills/poteto-help/SKILL.md", "| Build a page whose buttons wake a Grok Bot over a webhook | [`/make-bot-ui`](../make-bot-ui/SKILL.md) |\n", ""),

    # --- reflect / recall / automate-me: transcripts ---
    ("skills/reflect/SKILL.md", "ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10",
     "proj=~/.claude/projects/$(pwd | sed 's#[/.]#-#g')\nls -t \"$proj\"/*.jsonl \"$proj\"/*/subagents/*.jsonl 2>/dev/null | head -10"),
    ("skills/reflect/SKILL.md", "Reviewers return findings in the `Task` response body.", "Reviewers return findings in the `Agent` result."),
    ("skills/recall/SKILL.md",
     "Transcripts live at `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`, where `<slug>` is the workspace path with the leading slash dropped and each \"/\" turned into \"-\" (so `/Users/you/proj` becomes `Users-you-proj`).",
     "Transcripts live at `~/.claude/projects/<slug>/<session-id>.jsonl`, where `<slug>` is the working directory with every \"/\" and \".\" turned into \"-\" (so `/Users/you/proj` becomes `-Users-you-proj`)."),
    ("skills/reflect/references/judgment-reviewer.md", "a `Task` prompt naming its path", "an `Agent` prompt naming its path"),
    ("skills/reflect/references/tooling-reviewer.md", "a `Task` prompt naming its path", "an `Agent` prompt naming its path"),
    ("skills/reflect/references/divergent-reviewer.md", "a `Task` prompt naming its path", "an `Agent` prompt naming its path"),

    # --- playbooks: cloud agents, Cursor features ---
    ("skills/poteto-mode/playbooks/shipping.md", "each a Cursor cloud agent,", "each a background agent in its own worktree,"),
    ("skills/poteto-mode/playbooks/autopilot-full.md", "Each owner is a Cursor cloud agent that builds", "Each owner is a background agent, in its own worktree, that builds"),
    ("skills/poteto-mode/playbooks/babysit.md",
     " This playbook replaces Cursor's built-in babysit skill for these requests, so do not route there even though its description matches the same words.", ""),
    ("skills/poteto-mode/playbooks/multi-phase-plan.md", "Each live lane runs on its own cloud VM at the PR head.", "Each live lane runs in its own worktree at the PR head."),
    ("skills/poteto-mode/playbooks/orchestrate.md", "Spawn workers with `Task`.", "Spawn workers with `Agent`."),
    ("skills/poteto-mode/playbooks/worktree-cleanup.md", "lives at `.cursor/worktrees/myrepo/x`", "lives at `.claude/worktrees/x`"),

    ("skills/poteto-mode/playbooks/orchestrate.md",
     "Run workers on a new cloud VM (`isolation: \"worktree\"`) unless the work needs this machine: a `control-ui` or `control-cli` runtime check (from `cursor-team-kit`), local transcripts, a simulator, or auth that exists only here.",
     f"Run writers in a new worktree (`isolation: \"worktree\"`). A worker that only drives this machine's shared state runs without isolation: a `control-ui` or `control-cli` runtime check against a running app (see **Control skills** in {RT}), local transcripts, a simulator, or auth that exists only here."),
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
     "pstack is built for Cursor, and it also installs in Claude Code with `/plugin marketplace add cursor/plugins`, then `/plugin install pstack@cursor-plugins`. There, each command takes a `pstack:` prefix, such as `/pstack:poteto-mode`. The [Claude Code adapter](../../docs/harness/claude-code.md) maps the Cursor names, and a step that needs a Cursor-only feature, such as Bugbot or Automations, is skipped with a one-line note.\n\nOther tools can read the skills, because they use the Agent Skills format. But most workflow skills, including `/poteto-mode`, `/how`, `/why`, and `/teach`, spawn Cursor subagents with per-role models, and Custom Modes and `/loop` are Cursor features, so those parts may not work there.",
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
        elif not new:
            continue
        else:
            failed.append((rel, old[:90]))
    for rel, old in failed:
        print(f"MISSING in {rel}: {old!r}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
