#!/usr/bin/env python3
"""Mechanical Cursor -> Claude Code substitutions for an upstream pstack checkout.

Usage: python3 port/port.py <plugin-root>

Only safe, context-free rewrites live here. Hand edits (model panels, cloud
agents, Cursor-only features) are listed in port/PORTING.md and must be
re-applied after a re-port.
"""
import pathlib
import re
import sys

LITERAL = [
    ("~/.cursor/rules/pstack-models.mdc", "~/.claude/rules/pstack-models.md"),
    ("pstack-models.mdc", "pstack-models.md"),
    ("claude-opus-5-5-xhigh", "opus"),
    ("subagent_type: generalPurpose", "subagent_type: general-purpose"),
    ("`generalPurpose`", "`general-purpose`"),
    ("generalPurpose", "general-purpose"),
    ('"poteto-agent"', '"pstack:poteto-agent"'),
    ('"Comment Sicko"', '"pstack:comment-sicko"'),
    ("AskQuestion", "AskUserQuestion"),
    ("the Task tool", "the Agent tool"),
    ("`Task` call", "`Agent` call"),
    ("`Task` calls", "`Agent` calls"),
    ("Spawn `Task` with", "Spawn `Agent` with"),
    ("- `readonly`: `true`", "- read-only: say so in the brief (no edits, no writes)"),
    ("~/.cursor/plugins/", "~/.claude/plugins/"),
    (".cursor/skills/", ".claude/skills/"),
    ("~/.cursor/projects/*/", "~/.claude/projects/*/"),
    ("Cursor's built-in `create-skill` skill", "the `skill-creator` skill"),
    ("Cursor's built-in `create-skill`", "the `skill-creator` skill"),
    ("the **create-skill** skill (Cursor's built-in for authoring SKILL.md files)",
     "the **skill-creator** skill (Anthropic's skill-authoring skill)"),
    ("create-skill", "skill-creator"),
    ("the `deslop` skill from the `cursor-team-kit` plugin (`/deslop`)", "Claude Code's built-in `/simplify`"),
    ("`/deslop` from `cursor-team-kit`", "`/simplify`"),
    ("`/deslop`", "`/simplify`"),
    (" from `cursor-team-kit`", " (see **Control skills** in `poteto-mode/references/claude-code-runtime.md`)"),
    ("Cursor's `/loop` command", "Claude Code's `/loop` command"),
    ("Cursor restart", "Claude Code restart"),
    ("Cursor's Plan Mode", "Claude Code's plan mode"),
    ('environment: "cloud"', 'isolation: "worktree"'),
    ("grok-4.7-xhigh-fast", "sonnet"),
    ("grok-4.7-medium-fast", "sonnet"),
]

REGEX = [
    # Readonly-false lines exist only to keep MCP access; Claude Code subagents keep MCP either way.
    (re.compile(r"^- `readonly`: `false`.*\n", re.M), ""),
    (re.compile(r",? ?agent mode \(`readonly: false`\)\.( [^.]*MCP[^.]*\.)*( Readonly strips MCPs\.)?"), "."),
    # Transcript location: Cursor names it in the system prompt; Claude Code does not.
    (re.compile(r"(?:under|in) the active workspace's `agent-transcripts/` directory \(the system prompt names (?:this|the) path\.?\)?"),
     "in this project's Claude Code transcript directory (see **Transcripts** in `poteto-mode/references/claude-code-runtime.md`)"),
    (re.compile(r"The system prompt names the (?:active )?workspace's `agent-transcripts/` directory\. Use (?:only )?that path\."),
     "Find this project's transcript directory per **Transcripts** in `poteto-mode/references/claude-code-runtime.md`. Use only that directory."),
]


def port_text(text: str) -> str:
    for old, new in LITERAL:
        text = text.replace(old, new)
    for pattern, new in REGEX:
        text = pattern.sub(new, text)
    return text


def main() -> None:
    root = pathlib.Path(sys.argv[1])
    owned = {"skills/setup-pstack/SKILL.md", "skills/poteto-mode/references/claude-code-runtime.md"}
    for path in sorted(root.glob("skills/**/*.md")) + sorted(root.glob("agents/*.md")):
        if str(path.relative_to(root)) in owned:
            continue
        before = path.read_text()
        after = port_text(before)
        if after != before:
            path.write_text(after)
            print(f"ported {path.relative_to(root)}")


if __name__ == "__main__":
    main()
