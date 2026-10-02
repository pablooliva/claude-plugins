---
name: retro
description: "Retrospective on a development cycle: reads every session of the cycle (across /clear and compaction) plus the SDD records it left, and proposes changes to the agent's environment — automated checks, review standards, steering files, tooling, information access — so the next cycle goes better. Proposes only; changes nothing until you pick. User-invoked: `/retro [feature | branch | since <date> | session <id>]`."
disable-model-invocation: true
---

# Retro

The user has asked for a **retrospective**. You are suggesting improvements to the coding agent's **environment** so future runs go better. You are not reviewing the code the cycle produced (that is `/critical-review` or the flow's code review), and you are not recording what was learned about the feature (that is `sdd-flow`'s per-slice retrospective and its ledger). The question here is: *what about this repo and its setup let the struggle happen, and what check, standard, or tool would stop it happening again?*

**Propose only.** Present candidates; change nothing until the user picks one.

Adapted from `retro` in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT — see the plugin's `THIRD-PARTY-NOTICES.md`). Self-contained.

## Why a cycle, not a session

A development cycle rarely fits one session. Every `/clear` starts a new transcript, and a compaction hides earlier turns from you even though they are still on disk. In an `sdd-flow` run the main session only orchestrates — the struggle happens inside subagents whose transcripts you never saw. So what is in your context window is a small, late, unrepresentative slice of the cycle. **Do not run the retrospective from memory.** Gather the record first.

Three sources survive `/clear` and compaction:

1. **Session transcripts** — Claude Code keeps one JSONL file per session, and each session's subagent transcripts beside it. `scripts/session-digest.py` (in this skill's directory) lists a repository's sessions across all its worktrees and reduces each to the moments a retrospective needs.
2. **SDD records** in the repo, when the project uses `sdd-flow` — see [references/sdd-evidence.md](references/sdd-evidence.md). These outlive the transcripts, which Claude Code deletes after its retention period (30 days by default).
3. **Git history** of the cycle's branch.

## Steps

### 1. Scope the cycle

Resolve `SCRIPT` = `<this skill's directory>/scripts/session-digest.py` (the skill's base directory is shown when the skill loads; if it is not, use the highest version under `~/.claude/plugins/cache/pablooliva/agent-engineering/*/skills/retro/`).

Decide which sessions make up the cycle:

- **The user named it** — a feature, a branch, `since <date>`, or `session <id>`: use that.
- **Otherwise** — the cycle is the current git branch's work. On the default branch, where a branch filter selects everything, ask for a start date instead.

List the candidates, then show the user the rows you intend to read and let them correct the selection before you read anything. They know where the cycle began; you are inferring it.

```bash
python3 "$SCRIPT" list --branch "$(git branch --show-current)"      # this repo, every worktree
python3 "$SCRIPT" list --since 2026-09-20                           # by date instead
python3 "$SCRIPT" list --branch feat/cart --any-project             # the worktree was removed since
```

Drop rows with zero tool calls — they are housekeeping sessions, not work. If `list` finds nothing (transcripts expired, or a different machine), say so and continue with sources 2 and 3 alone.

### 2. Read the record

Digest the selected sessions. The digest is the map, not the evidence: each item carries a transcript line number (`L<n>`).

```bash
python3 "$SCRIPT" digest <session-id> [<session-id> ...]
```

- For more than about five sessions, digest in batches and note candidates as you go rather than holding every digest at once.
- When an item looks like a real struggle — a correction from the user, a failed call repeated, a long lookup run, an oversized result — read that moment in full before you build a candidate on it: `sed -n '<n>,<m>p' <transcript> | cut -c1-3000`. For a subagent, digest its own file (`digest <path to agent-*.jsonl>`).
- The user's prompts are the highest-value lines. A prompt that corrects, repeats, or re-explains is a struggle the agent may not have noticed.

If the repo has an `SDD/` directory, read [references/sdd-evidence.md](references/sdd-evidence.md) and gather what it lists for this feature. Then skim `git log --stat <base>..HEAD` for fix-ups, reverts, and files that changed again and again.

Transcripts and digests can quote secrets and private data. Keep them in the conversation; never write them, or excerpts of them, into the repo.

### 3. Find candidates

Every candidate must cite **a specific moment** — a session id and line, a review finding, a compaction file, a commit. A candidate you cannot trace to a moment is generic advice: discard it. An empty category is a normal result; do not fill categories to look thorough.

- **Navigation** — did the agent take a long time to find a file or fact, or miss a hidden dependency between files? Fix the cause where the agent already looks: rename or co-locate so the thing is where its name says, put a comment at the dependency site, or add a README beside the code. A line in `CLAUDE.md` is the last resort and only for a convention the agent *cannot* infer from the code — never a file listing or an architecture map. _Use when_ a lookup run was long, or a subagent hit its read budget (a Safety-Net compaction).
- **Automated checks** — could a check have caught a mistake the agent made? Read the repo's own check commands first (its `lint`/`check`/test scripts, its CI workflow), so a check that exists but sits unwired or silently broken is the finding, not a reinvention. A repo with no **guardrail** at all — no pre-commit hook and no CI job running its lint/typecheck/test command — is itself a finding. _Use when_ the agent made a mistake a machine could have caught, the same review finding recurs across slices or features, or the repo has no guardrail.
- **Review standards** — did a reviewer miss a mistake, or catch the same judgement call again and again? Classify the violation first. A **mechanical** one (a fixed syntactic pattern, a banned API, an import shape, a file-location rule) gets a deterministic check, full stop — a rule in the repo's own linter, a pre-commit hook, or a CI job, whichever is cheapest given what the repo already has. Only a genuine **judgement call** (cross-file consistency, "matches the surrounding style") becomes prose, and it goes where the reviewer reads it — see *Where standards go* below. _Use when_ a mistake reached review or got past it.
- **Steering files** — is there an instruction in `CLAUDE.md`/`AGENTS.md` (repo or global) that was in context and visibly did nothing, or that is really a mechanical rule or a review standard? Report the instruction and the moment, and recommend running the `improve-claude-md` skill for the edit; do not audit the file yourself. _Use when_ a steering instruction was ignored, or the file is large.
- **Tool economy** — did the agent make expensive calls that could be streamlined? Is a custom CLI, script, or MCP tool returning far more than the agent needs? _Use when_ the digest shows an oversized result or a command run many times.
- **Information access** — was a crucial piece of information out of the agent's reach? Teeing dev-server logs to a file, read-only access to a third-party service, a seeded local database. _Use when_ the agent guessed, or the user had to paste something in.

### 4. Present

Present the candidates to the user in order of severity. For each: the category, the moment(s) it comes from, the proposed change and where it would live, and what it costs to build. Then stop. Build a candidate only when the user picks it, and try a new check against the repo before it is allowed to block anything.

## Reference

### Implementation vs review

All work goes through two stages. The implementing agent carries the most **context pressure**: it explores, writes code, and debugs failures. The reviewing agent receives a diff, so it needs no exploration. Standards therefore belong to the **reviewer**, not the implementer — and never in a file loaded into every session.

### Where standards go

A judgement-call rule must land where a reviewer will actually walk it. `sdd-flow`'s code review and slice review look for the project's review checklist in a fixed order and walk the first one found: an explicit path in the spawn prompt, a checklist section in the root `CLAUDE.md`/`AGENTS.md`, the same in a nearer `CLAUDE.md`, a root `CODING_STANDARDS.md`, then the PR template.

- **The project already has a checklist** in one of those places: add the rule there.
- **It has none:** propose creating `CODING_STANDARDS.md` at the repo root. It is read during review, not implementation, so it costs the implementer nothing.

### Steering files

`improve-claude-md` owns what belongs in `CLAUDE.md`/`AGENTS.md`: preferences, behavioural nudges, corrections, and conventions the agent cannot infer — not discoverable facts such as file locations or structure. When this retrospective's advice and that skill's principles disagree, that skill wins.

### Limits

- The retrospective sees one cycle. It cannot tell that a check added last month has gone noisy or outlived its bug; pruning checks stays the user's job.
- Severity order is a first draft: a quiet, expensive mistake can rank below a loud, cheap one.
- A smooth cycle has little to teach. Saying "nothing worth changing" is a valid outcome.
