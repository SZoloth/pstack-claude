# Claude Code runtime notes

pstack was written for Cursor. This file maps every Cursor mechanism the skills assume onto Claude Code. When a skill and this file disagree about mechanics, this file wins. Skills still own the workflow.

## Finding pstack files

pstack is a Claude Code plugin. Its skills are namespaced: the user types `/pstack:how`, `/pstack:poteto-mode`, and so on. A bare `/how` works only when no other skill has that name.

Most pstack skills set `disable-model-invocation: true`, so the Skill tool will not load them. Read them by path instead. When a skill loads, Claude Code prints its base directory. Every sibling skill lives at `<base directory>/../<skill-name>/SKILL.md`, and the plugin root is `<base directory>/../..`. If you have no base directory (for example, inside a subagent), locate the root with:

```bash
dirname "$(dirname "$(ls -d ~/.claude/plugins/cache/*/pstack/*/skills/poteto-mode 2>/dev/null | tail -1)")"
```

When you spawn a subagent that must read pstack files, pass it the absolute plugin root in the brief.

## Spawning subagents

Cursor's `Task` tool is Claude Code's `Agent` tool. Map the fields this way:

| Cursor field | Claude Code |
|---|---|
| `subagent_type: generalPurpose` | `subagent_type: "general-purpose"` |
| `subagent_type: "poteto-agent"` | `subagent_type: "pstack:poteto-agent"` |
| `subagent_type: "Comment Sicko"` | `subagent_type: "pstack:comment-sicko"` |
| `model: <slug>` | `model` from the role value (see **Model values**) |
| `readonly: true` | No flag exists. Say "read-only: do not edit or write files" in the brief, or use `subagent_type: "Explore"` for pure search. |
| `readonly: false` | The default. Claude Code subagents keep MCP access either way. |
| `run_in_background: true` | Same field. You are notified when the agent finishes. Do not poll. |
| `environment: "cloud"` | `isolation: "worktree"` for an isolated checkout on this machine. Use `isolation: "remote"` only when the session offers it and the worker needs nothing local. |
| `environment: "local"` | Omit `isolation`. |
| `cloud_base_branch` | Tell the worker to `git checkout <branch>` in its worktree as its first step. |
| Resume an agent | `SendMessage` to the agent's name or id. |

"Cloud agent" in a skill means an isolated worker. In Claude Code that is a background `Agent` with `isolation: "worktree"`. A worktree worker shares this machine's CPU, so cap a fan-out at about 6 concurrent workers and queue the rest.

## Model values

The `~/.claude/rules/pstack-models.md` rule (written by `/pstack:setup-pstack`) assigns a value to each role. Valid values:

| Value | Family | How to spawn it |
|---|---|---|
| `fable`, `opus`, `sonnet`, `haiku` | claude | `Agent` with that `model`. |
| `inherit` (also `inherit-parent`, `auto`) | parent's | `Agent` with `model` omitted. |
| `codex` | gpt | A thin `Agent` wrapper (`model: "sonnet"`) that runs the Codex CLI and returns its output. See **Codex seats**. |

A value may carry an effort suffix, such as `opus:xhigh` or `codex:high`. Pass the suffix as the `Agent` tool's `effort` field (the rule file counts as the user's explicit instruction to set it). For a `codex` seat, pass it as `-c model_reasoning_effort=<effort>` (Codex accepts `minimal`, `low`, `medium`, `high`, `xhigh`; map `max` to `xhigh`).

A **different model family** means `claude` versus `gpt`. Opus versus Sonnet is the same family. Panels (`arena`, `architect`, `interrogate`), cross-judges, and "verify on a different model family" steps need one seat from each family when both are available.

If `command -v codex` fails, a `codex` seat falls back to `opus` and you say in the reply that the panel lost its cross-family seat. Never fall back silently.

### Codex seats

Spawn a `codex` seat as an `Agent` with `subagent_type: "general-purpose"`, `model: "sonnet"`, `effort: "low"`, and this brief:

```
You are a thin wrapper around the Codex CLI. Do not do the task yourself.
1. Write the task below, verbatim, to a temp file.
2. Run: codex exec <SANDBOX> -C <REPO_OR_WORKTREE> -o <OUT_FILE> [-c model_reasoning_effort=<EFFORT>] "$(cat <TEMP_FILE>)"
   Use a timeout of 600000 ms and run it in the background if it may run longer.
3. Return the contents of <OUT_FILE> verbatim, then one line with the exit code.
TASK:
<the seat's full prompt>
```

`<SANDBOX>` is `-s read-only` for reviewers, judges, explorers, and investigators. It is `--full-auto` for a writer, and a writer always runs in its own worktree. After any Codex writer finishes, run `git status` in its worktree. Codex can create files or commits you did not ask for.

## Asking the user

Cursor's `AskQuestion` is Claude Code's `AskUserQuestion`: 1 to 4 questions, 2 to 4 options each, with an automatic "Other" option.

## Todo list

Where a skill says "open a todo list", use Claude Code's task or todo tool if the session has one. Otherwise keep the list in your reply.

## Transcripts

Claude Code stores each session as `~/.claude/projects/<slug>/<session-id>.jsonl`. `<slug>` is the absolute working directory with every `/` and `.` replaced by `-`, so `/Users/you/proj` becomes `-Users-you-proj`. Subagent transcripts live under `<slug>/<session-id>/subagents/`. The newest `.jsonl` in the directory is usually the current session.

```bash
proj=~/.claude/projects/$(pwd | sed 's#[/.]#-#g')
ls -t "$proj"/*.jsonl | head -5
```

Read only the current project's directory. Do not glob across `~/.claude/projects/*/`. That reads private chats from unrelated projects.

## Control skills

pstack refers to `control-ui` and `control-cli`, which ship in Cursor's `cursor-team-kit`. In Claude Code, use whichever of these the session has:

- **control-ui** (browser, Electron, web UIs). The built-in browser tools (`mcp__Claude_Browser__*`, with `preview_start` for a dev server from `.claude/launch.json`), Claude in Chrome (`mcp__claude-in-chrome__*`), or a browser skill such as `agent-browser` or `webapp-testing`. For native macOS apps, computer use (`mcp__computer-use__*`). For iOS, the iOS Simulator tools.
- **control-cli** (CLIs and TUIs). Run the CLI through Bash and capture its output. Drive a TUI in a `tmux` session with `tmux send-keys` and read it with `tmux capture-pane -p`.

If the project has its own `verify-*` skill under `.claude/skills/`, prefer it.

## Built-ins that differ from Cursor

| Cursor | Claude Code |
|---|---|
| `/deslop` (`cursor-team-kit`) | `/simplify` (built in) |
| `create-skill` | the `skill-creator` skill |
| `/loop` | `/loop` (built in; self-paced when you omit the interval) |
| Plan Mode | plan mode |
| Custom Modes (option+enter keeps a skill on every turn) | No equivalent. Invoke `/pstack:poteto-mode` at the start of each task. |
| Cursor's built-in babysit skill | None. The Babysit playbook is the only one. |
| `~/.cursor/rules/*.mdc` with `alwaysApply: true` | `~/.claude/rules/*.md`, or an `@`-import from `~/.claude/CLAUDE.md` |
| `.cursor/skills/`, `~/.cursor/skills/` | `.claude/skills/`, `~/.claude/skills/` |
| Cursor dashboard for cloud-agent status | The background task list, or `claude.ai/code` for remote sessions |
| Listing MCPs from the `mcps/` directory | Tools named `mcp__<server>__*` in this session, plus deferred tools you can find with `ToolSearch` |
| Bugbot | Still works. It is a GitHub app that comments on PRs, independent of the editor. |
