# Claude Code runtime notes

pstack was written for Cursor. This file maps every Cursor mechanism the skills assume onto Claude Code. When a skill and this file disagree about mechanics, this file wins. Skills still own the workflow.

## Finding pstack files

pstack is a Claude Code plugin. Its skills are namespaced: the user types `/pstack:how`, `/pstack:poteto-mode`, and so on. A bare `/how` works only when no other skill has that name.

Most pstack skills set `disable-model-invocation: true`, so the Skill tool will not load them. Read them by path instead, and where a skill says "run `/x`", read `<pstack-root>/skills/x/SKILL.md` and follow it. When a skill loads, Claude Code prints its base directory. `<pstack-root>` is `<base directory>/../..`. If you have no base directory (for example, inside a subagent), get it with:

```bash
python3 -c "import json,os;d=json.load(open(os.path.expanduser('~/.claude/plugins/installed_plugins.json')))['plugins'];e=sorted((i for k,v in d.items() if k.startswith('pstack@') for i in v),key=lambda i:i.get('scope')!='user');print(e[0]['installPath'] if e else 'PSTACK_NOT_INSTALLED')"
```

When you spawn a subagent that must read pstack files, pass it the absolute `<pstack-root>` in the brief.

Paths in skills and playbooks are relative to pstack, never to the user's repo. `pstack/skills/...` means `<pstack-root>/skills/...`. `scripts/...` inside a poteto-mode playbook means `<pstack-root>/skills/poteto-mode/scripts/...`. A step that says `git show origin/main:pstack/<path>` means read `<pstack-root>/<path>`.

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
| `cloud_base_branch` | The worker's first step is `git fetch origin <branch> && git switch -C <worker-branch> origin/<branch>` in its worktree, with a worker-branch name of its own. A plain checkout of `<branch>` fails when that branch is checked out elsewhere. |
| Resume an agent | `SendMessage` to the agent's name or id. |

"Cloud agent" in a skill means an isolated worker. In Claude Code that is a background `Agent` with `isolation: "worktree"`. A worktree worker shares this machine's CPU, so cap a fan-out at about 6 concurrent workers and queue the rest.

## Model values

The `~/.claude/rules/pstack-models.md` rule (written by `/pstack:setup-pstack`) assigns a value to each role. Valid values:

| Value | Family | How to spawn it |
|---|---|---|
| `fable`, `opus`, `sonnet`, `haiku` | claude | `Agent` with that `model`. |
| `inherit` (also `inherit-parent`, `auto`) | parent's | `Agent` with `model` omitted. |
| `codex` | gpt | A background Bash job running `codex-seat.sh`, not an `Agent`. See **Codex seats**. |

### Parsing a role value

Every skill that reads a role line resolves its value this way. Never pass the raw value to `model`.

1. Split `name[:effort]` on the colon. `opus:xhigh` is name `opus`, effort `xhigh`.
2. `inherit`, `inherit-parent`, or `auto`: omit `model`.
3. `codex`: run a Codex seat, passing the effort to the script.
4. Anything else: `model: "<name>"`.
5. For an `Agent` spawn with an effort, pass it as the `effort` field. (A `codex` seat takes the effort as a script argument instead.) The rule file counts as the user's explicit instruction to set it.

Skill defaults carry no effort suffix, so they run at the session's effort.

A **different model family** means `claude` versus `gpt`. Opus versus Sonnet is the same family. Panels (`arena`, `architect`, `interrogate`), cross-judges, and "verify on a different model family" steps need one seat from each family when both are available.

### Codex seats

A Codex seat is not a subagent. Run it yourself, in the same message as the panel's other spawns:

1. Write the seat's full prompt to a file in your scratchpad.
2. Run this with Bash, `run_in_background: true`, `timeout: 600000`:
   ```bash
   <pstack-root>/skills/poteto-mode/scripts/codex-seat.sh <read-only|workspace-write> <dir> <effort or -> <prompt-file> <out-file>
   ```
   Use `read-only` for reviewers, judges, explorers, and investigators. Use `workspace-write` for a writer, and point `<dir>` at that writer's own worktree (`git worktree add`).
3. You are notified when it exits. Its output is the seat's report.

The script stops on Codex's output file, not on process exit, because Codex can keep running after it has answered. It caps a run at 9 minutes (`CODEX_SEAT_TIMEOUT`, in seconds), just under the Bash tool's 10-minute limit. If the harness kills it anyway, it still prints `CODEX_SEAT_LOST`.

If the output starts with `CODEX_SEAT_LOST`, rerun that seat as an `opus` `Agent` and say in the reply that the panel lost its cross-family seat and why. Never fall back silently. After a Codex writer finishes, run `git status` in its worktree. Codex can create files or commits you did not ask for.

## Asking the user

Cursor's `AskQuestion` is Claude Code's `AskUserQuestion`: 1 to 4 questions, 2 to 4 options each, with an automatic "Other" option.

## Todo list

Where a skill says "open a todo list", use Claude Code's task or todo tool if the session has one. Otherwise keep the list in your reply.

## Transcripts

Claude Code stores each session as `~/.claude/projects/<slug>/<session-id>.jsonl`. `<slug>` is the absolute working directory with every `/` and `.` replaced by `-`, so `/Users/you/proj` becomes `-Users-you-proj`. Subagent transcripts live under `<slug>/<session-id>/subagents/`. The newest `.jsonl` in the directory is usually the current session. Each line is one JSON record. The first line is often bookkeeping (`"type":"queue-operation"`), so find the opening prompt in the first record with `"type":"user"`, under `message.content` (a string, or a list whose `text` items hold the prompt).

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
