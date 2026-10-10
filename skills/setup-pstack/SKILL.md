---
name: setup-pstack
description: Configure which models pstack uses per role and at what reasoning budget. Detects your available models (Claude tiers plus the Codex CLI) and writes an always-loaded rule that overrides the skill defaults. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

Write `~/.claude/rules/pstack-models.md`, a rule file Claude Code loads into every session, that sets pstack's model per role. Value syntax and spawn mechanics live under **Model values** in `../poteto-mode/references/claude-code-runtime.md`. Read that section first.

## Steps

### 1. Detect available models

- Claude tiers: `opus`, `sonnet`, and `haiku` are always valid `Agent` models. `fable` is valid when the session's model list includes Fable. If unsure, spawn a one-line `Agent` with `model: "fable"` and treat an error as unavailable.
- Codex: run `command -v codex && codex --version`. If it succeeds, `codex` is available. If not, say that panels will have no cross-family seat until the user installs the Codex CLI.
- `inherit` is always valid.

### 2. Load current state

The default role-to-model mapping is the rule shape in step 5. If `~/.claude/rules/pstack-models.md` exists, read it and treat its `budget:` line and role values as the current choices. Otherwise start from the defaults. A line whose role is not in step 5 is from a retired role. Drop it.

### 3. Budget, map, and confirm

**(a) Ask for a budget** with `AskUserQuestion`. Offer these four options with these exact labels, and name the current budget when the rule records one. With no rule, say that `large` matches the skill defaults.

- `unlimited — max effort`
- `large — xhigh effort`
- `medium — high effort`
- `small — medium effort`

**(b) Apply it.** Build the working table from the defaults, and on a re-run keep any role the user changed. The budget sets the effort suffix on every non-`inherit` value: `unlimited` → `:max`, `large` → `:xhigh`, `medium` → `:high`, `small` → `:medium`. `codex` caps at `xhigh`, so `unlimited` writes `codex:xhigh`. Under `small`, also move code-delegate roles from `opus` to `sonnet` if any were set to `opus`.

**(c) Show the roles and confirm.** Show every role with its value, and list each line step 2 dropped. Ask with `AskUserQuestion` whether to accept as-is or change specific roles. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, one subagent per entry, so the list length sets the count. Keep one `claude` and one `gpt` entry on each panel when Codex is available. `arena cross-judge pool` is a list from which Arena picks one value whose family differs from the parent's.

### 4. Validate

Every value written must be a detected model, `codex` (only if detected), or `inherit`, each with an optional effort suffix from `low`, `medium`, `high`, `xhigh`, `max`. If a chosen value is unavailable, stop and ask again.

### 5. Write the rule

Write `~/.claude/rules/pstack-models.md`. Overwrite the whole file so re-runs stay idempotent. Shape (shown at the `large` budget):

```
# pstack model configuration

pstack skills read this file for per-role models. One line per role. Delete a line to fall back to the skill default.
Values: fable | opus | sonnet | haiku | codex | inherit, with an optional effort suffix (opus:xhigh).
`codex` runs as a background Bash job via skills/poteto-mode/scripts/codex-seat.sh. `inherit` runs on the session's model (omit `model`).
Spawn mechanics: poteto-mode/references/claude-code-runtime.md in the pstack plugin.

budget: large (xhigh)
feature, refactoring: sonnet:xhigh
bug-fix: sonnet:xhigh
perf-issue: sonnet:xhigh
hillclimb: sonnet:xhigh
judgment and prose: opus:xhigh
hardest tasks: opus:xhigh
how explorer: sonnet:xhigh
how explainer: opus:xhigh
why investigators: sonnet:xhigh
why synthesizer: opus:xhigh
reflect tooling: sonnet:xhigh
reflect judgment, divergent, synthesizer: opus:xhigh
arena runners: opus:xhigh, codex:xhigh
arena cross-judge pool: opus:xhigh, codex:xhigh
swarm workers: sonnet:xhigh
architect runners: opus:xhigh, codex:xhigh
interrogate reviewers: opus:xhigh, codex:xhigh
```

If Fable is available, offer it for `judgment and prose` and `hardest tasks`. If Codex is not available, write `opus` in place of each `codex` entry and add a comment line saying the panels lack a cross-family seat.

### 6. Confirm

Tell the user the rule was written and that it loads in new sessions. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill under `.claude/skills/`, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /pstack:create-verification-skill." On yes, read `../create-verification-skill/SKILL.md` and follow it. On no, move on without pushing.
