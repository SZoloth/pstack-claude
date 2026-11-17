# pstack-claude: what the harness posts mean for this repo

Repo: SZoloth/pstack-claude (public). Written 2026-11-16 from the default branch as it stood that day. Nothing was changed on GitHub.

## Source

- Post: [Shishira (@ShishiraReddy05), Nov 16, 2026](https://x.com/ShishiraReddy05/status/2122327324632686967). She had asked the night before for beginner material on harness engineering, then posted three X articles as "must read". No thread; her only other reply says she wants "content which help build own harness".
- [Theo, "What is a 'harness'?"](https://x.com/theo/status/2113424203345265053) (Oct 23, 2026)
- [Harrison Chase, "Your harness, your memory"](https://x.com/hwchase17/status/2042978500567609738) (Apr 11, 2026), which leans on [Sarah Wooders, "Why memory isn't a plugin (it's the harness)"](https://x.com/sarahwooders/status/2040121230473457921) and LangChain's ["The Anatomy of an Agent Harness"](https://blog.langchain.com/the-anatomy-of-an-agent-harness/)
- [Mohit Goyal, "I Built an Agentic Harness From Scratch"](https://x.com/ByteMohit/status/2063493300884246598) (Jun 7, 2026), with code at [MohitGoyal09/AgentForge](https://github.com/MohitGoyal09/AgentForge)

## What the sources say

**Theo: the harness is the plumbing, not the app.** A model only emits text. The harness is five things: tools that do work, a text syntax for calling them, a parser that spots calls and runs code, a way to return results to the model, and a list of tools with descriptions. Claude Code and Codex are an interface wrapped around a harness (Agent SDK, Codex App Server). Tools run inside the harness; MCP servers run "somewhere else" and are reached over a protocol. His kitchen analogy: model is the chef, harness is the kitchen, an app like T3 Code is a restaurant that lets you bring any kitchen. T3 Code exposes its cross-harness features (Claude threads spawning Codex subagents) as one MCP server instead of writing a plugin for every harness. "An agent is a harness plus an LLM," and most "different agents" are the same harness with different tools, instructions and MCP servers.

**Chase and Wooders: whoever owns the harness owns the memory.** Memory is context, and context management is the harness's core job. Wooders lists the hidden decisions a harness makes: how AGENTS.md or CLAUDE.md is loaded, how skill metadata is shown, whether the agent can edit its own instructions, what survives compaction, whether past interactions are stored and searchable, how much of the filesystem and working directory is exposed. Chase's ladder of lock-in: stateful APIs (server-side compaction, Responses API threads) are mildly bad; closed harnesses with unknown memory artifacts are bad; a whole harness plus long-term memory behind an API (Claude Managed Agents) is worst. Codex is open source but its compaction summary is encrypted and unusable elsewhere. His own email agent got deleted and the rebuilt one was far worse because the learned preferences were gone. The prescription: keep memory in open formats you control (AGENTS.md, skills, your own store) so you can switch models and harnesses. The LangChain post adds the standard component list: filesystem and git for durable state, bash as a general tool, sandboxes, memory files, compaction, offloading big tool outputs to files (keep head and tail), skills as progressive disclosure, Ralph loops (a hook that catches the model's attempt to stop and re-injects the goal), and planning plus self-verification.

**Goyal: the model is about 20% of the engineering.** "An agent is a runtime that controls how a model sees, acts, retries, remembers, and stops." The concrete techniques from AgentForge:

- *Session first.* Build the model's world (tools, MCP tools, visible skills, mode) before the first call.
- *The loop is a control system.* Turn budgets (smaller in plan mode), ordered model fallbacks with a circuit breaker that stops calling a failing provider, context-pressure checks with compaction, and a `LoopDetector` that flags three identical tool calls in a row or a repeating cycle of 2 to 5 actions and forces a final answer.
- *Tool results are observations, not logs.* Every tool returns a `ToolResult` with `summary`, `artifacts`, `next_actions` and `recovery_hint`; failures go through an `error_result` factory that fills in a default hint ("inspect the current state ... retry only if the action is still safe").
- *One registry pipeline.* Every result, local or MCP, passes cleanup, secret redaction, untrusted-content wrapping and hooks before the model sees it.
- *File tools expose hidden state.* Line numbers, offset/limit, binary detection, a truncation flag, trailing-newline status. Edits require a unique exact match and, on a miss, show similar lines and say "re-read, your copy may be stale". Patches reject absolute paths and `..`, and dry-run with `git apply --check`.
- *Approval is policy, not a vibe.* Modes (on-request, auto, auto-edit, never, yolo) classify commands, paths and danger flags in plain code. Plan mode removes write tools from the schema list, so the model can't call them at all.
- *Tool output is evidence, not authority.* File reads, shell output, web pages and MCP responses get wrapped as `<untrusted_content source=...>` with a note to treat it as data. (Its wrapper does not escape a forged closing tag inside the content, so it is a label, not a sandbox, which the author admits.)
- *Context is not a transcript.* Track token estimates, prune old tool output, compact older turns into a continuation summary that lists completed work, and count compaction's own token cost.
- *Skills are context budgeting.* `discover()` builds a metadata index; `load_skill()` spends context only when a skill is chosen.
- *MCP tools get namespaced* (`github__create_issue`) and go through the same registry, approvals and wrapping as built-in tools.
- *Subagents are tools first.* One goal in, one result out, scoped tools, max turns, hard timeout, read-only by default. Swarms are a later, separate problem.
- *Persistence is systems work.* Atomic writes, owner-only permissions, append-only JSONL event logs, and tests that run against an isolated home directory because his session tests were silently reading his real `~/Library/Application Support` state.
- *Test the boundaries, not the prose.* 278 tests, none needing a model call: blocked commands, secret stripping, unique-match edits, plan-mode filtering, snapshot round-trips, wrapper coverage.

His starter checklist: one model adapter, a loop with stop conditions, three typed tools, structured results with recovery hints, approval before writes, line-numbered reads, context pruning, one checkpoint, one skill, one namespaced MCP server, and one test where a tool fails and the model still gets a useful observation.

## What this repo is

Public. A Claude Code port of poteto's pstack (upstream 0.15.36): 23 playbooks routed by `poteto-mode`, review panels, fan-outs and 24 one-rule principle skills, packaged as a Claude Code plugin. A GitHub Action (`.github/workflows/sync-upstream.yml`) re-runs `port/sync.sh` daily and applies `port/hand_edits.py`; the runtime mapping the skills read is `skills/poteto-mode/references/claude-code-runtime.md`.

This is skill scaffolding: workflows and principles loaded into someone else's harness. Most content changes belong upstream, because the sync overwrites anything outside the hand-edit layer.

## What applies

- **Skills as context budget.** Forty-plus skills means forty-plus descriptions in every session's skill index. AgentForge's discover/load split and the LangChain progressive-disclosure point both say the index should stay small. Add a check to the sync Action that totals description length across `skills/*/SKILL.md` and fails if it grows past a set budget or if any one description runs past a few hundred characters. That catches upstream growth before it reaches users.
- **Second-model review output is untrusted input.** Panels include a Codex seat run as a background Bash job (`skills/poteto-mode/scripts/codex-seat.sh`, `read-only` for reviewers). Codex reads the repo under review, which can contain instructions, and its output file comes back into the Claude session. Add a line to the Codex seats section of `claude-code-runtime.md` saying seat output is review text to weigh, not instructions to follow.
- **Already matches:** workers use `isolation: "worktree"`, fan-outs are capped at about 6, Codex seats are capped at 9 minutes, and a lost seat (`CODEX_SEAT_LOST`) falls back to an `opus` Agent with a rule to never fall back silently. That is Goyal's bounded subagents and visible fallback, done right.

## What doesn't apply

- Loop detection, approval, file tools, compaction. Claude Code provides them; pstack is instructions on top.
- Chase's memory point. pstack keeps no memory of its own beyond `~/.claude/rules/pstack-models.md`.
