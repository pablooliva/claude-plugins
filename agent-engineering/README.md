# agent-engineering

Cross-cutting skills and commands for disciplined AI-assisted software development, based on the [10 Claude Code Principles](https://jdforsythe.github.io/10-principles/) by JD Forsythe. Every skill and command here is independently usable in any session.

## Philosophy

This plugin provides the *agent-engineering discipline* that operates across any methodology — feedback loops, institutional memory, specialist review, token economy, and observability. Its flagship is `sdd-flow`: a self-contained, end-to-end Specification-Driven Development orchestrator that drives a feature from Research → Design gate → Planning → Implementation → Done through subagents with a fresh context window per phase, stopping after research for you to approve a short design brief.

## Self-contained as of 1.0.0

`sdd-flow` is a **permanent fork** of the SDD plugin's content, adapted for orchestrated (subagent-driven) execution. It is the **single source of truth for the flow** and depends on nothing outside this plugin at runtime:

- **Phase bodies** — the complete instruction set each spawned subagent reads lives under `skills/sdd-flow/bodies/` (one file per phase/review/capture step). The orchestrator passes each body **by absolute path** ("read this first"); it never pastes body content into a prompt and never reads from the SDD plugin's cache.
- **Agents** — the ten routed subagent types ship in `agents/` (`sdd-workhorse` at Sonnet, the eight `sdd-spec-*-specialist` agents at Sonnet, `sdd-critical-reviewer` at Opus). Model routing of every writing and fixing step is carried entirely by agent frontmatter — no runtime model switching. Review steps go first to a second model family through its CLI (3.9.0); the shipped reviewer agents are the fallback.
- **Hook** — `hooks/log_subagent_call.py` logs subagent transcripts via a `SubagentStop` hook registered in this plugin's `plugin.json`.

**The SDD plugin is no longer required and need not be installed.** The SDD plugin remains frozen at 2.2.0 as a standalone, human-driven methodology for its external users; this fork diverges from it deliberately so each can evolve independently. Nothing in `sdd-flow` references `/sdd:` commands or the SDD plugin cache.

### Why a permanent fork (rather than depending on SDD)

Before 1.0.0, `sdd-flow` embedded SDD command bodies at runtime and relied on SDD's shipped agents. That coupling meant a version skew between the two plugins could silently misbehave, and the orchestrated path could not diverge from the interactive SDD commands even where orchestration demanded it (e.g., a subagent cannot spawn or invoke slash commands, so "delegate to an Explore subagent" instructions had to become inline work). Forking permanently removes the dependency, lets the flow own its own evolution, and lets the SDD plugin stay stable for the people who use it directly.

### Architecture (1.0.0)

- **One-level spawning.** Every spawn happens at the orchestrator (main-conversation) level; spawned subagents must not spawn subagents and must not invoke slash commands or skills. Every body is pre-adapted for inline execution. *(Was a platform limit on Claude Code ≤2.1.171; since 2.1.172 the platform allows nesting to depth 5 — the flat design is retained deliberately. See `proposals/nested-subagents-analysis-2026-06-12.md` before refactoring toward nesting.)*
- **Two-stage specialist panel.** During planning, the orchestrator spawns one specialist subagent per `review_panel:` value in parallel (Stage 1; each writes a `PANEL-FINDINGS-*` file), then one `sdd-critical-reviewer` synthesis subagent reads those files from disk and emits the verdict (Stage 2). The bounded fix-and-re-review loop (max 3 iterations, progress-stall halt) is unchanged.
- **Reads-only safety net.** Spawned subagents do not spawn in this flow, so there is no nested-subagent counter — the only safety-net signal is file Reads (default trigger >15; >20 for implementation chunks). On trip, the subagent compacts and hands off.
- **Per-slice authoring default.** The planning body sets `delivery_mode: per-slice` unless the feature yields fewer than 2 genuine vertical slices (then `whole-feature` with a one-line justification). The PARSE default (frontmatter absent → whole-feature) is unchanged for backward compatibility.
- **Gated AI-agent security review (2.1.0).** Spec frontmatter `agent_security: auto|true|false` gates three hook points: the `agent-security` panel value at Step 3c (spec-level checks), the Agentic-Surface Lens in the Step 4b / per-slice code review (code-level checks), and the OWASP abuse cases the final check (4e.5) verifies as security rules. `auto` resolves by detecting an agentic surface — a model call, a tool/MCP definition, agent memory or a retrieval store, inter-agent messaging, or a model output driving an external action.
- **Design gate (3.4.0).** After research, one Opus subagent writes a **design brief** — at most 150 lines, in plain language: what will be built, how it will work, the decisions made and what was rejected, where the changes land, and what you must decide. The flow stops and shows it; nothing is specified until you approve it, and `approve` is refused while any of its questions is unanswered. The spec is then held to the brief: every departure is recorded, checked by the spec critical review, and shown to you before implementation starts. Each code review reports which changed files fall outside the footprint you approved.
- **Tiered delivery (3.4.0).** The brief proposes three delivery tiers — POC-plus, Standard, Full — and builds Tier 1 unless you choose otherwise. The spec covers the chosen tier only and lists what it deferred; reviewers treat that list as deliberate, and flag anything unsafe to defer or built ahead for a later tier. Every tier is reviewed in full. Each tier is its own cycle: `/sdd-flow --next-tier <feature>` starts the next one from feedback on the last. The rules are the `simplicity-challenge` skill's `references/tiers.md`, read by the flow and not restated.
- **One security check at the end (4.1.0).** After every fix has landed, a second model reads each security rule of the spec for a path on which it does not hold; each gap is fixed with a test that fails when its guard is removed, at most two rounds before you decide. The same final check runs the whole suite, reads the tests once more, and repeats the trace and eval checks when their gates are on. Every review passes with no HIGH or MEDIUM finding; LOW findings are listed for you, not fixed.
- **A picture of the cycle.** [`docs/sdd-flow-diagram.md`](docs/sdd-flow-diagram.md) draws the stages, what each one does and writes, and every place the flow stops for you.
- **Progressive disclosure.** `SKILL.md` is a slim orchestrator core; per-phase detail lives in `skills/sdd-flow/phases/` (`setup`, `research`, `planning`, `implementation-whole-feature`, `implementation-per-slice`, `protocols`), read at each phase boundary.

## Contents

### Skills

- **`sdd-flow`** — Self-contained end-to-end SDD lifecycle orchestration (see above).
- **`sdd-lite`** — A light alternative to `sdd-flow` for work whose requirements can be settled in one short interview. Builds in the main conversation with no subagents: an interview only for what is open, a one-page brief of your decisions that you approve (the one gate), the build with tests, one Codex review of every change (and one check of its fixes, no further rounds), and a close-out that keeps the records later cycles read: a decision record through `cross-cutting-adr` when a choice binds later work, glossary updates, and the brief under `SDD/briefs/`. Writes no research, spec, slices, site counts, review reports or run logs. Tells you to switch to `sdd-flow` when the requirements stay unclear or the work needs slices. `/sdd-lite <task>`. [`docs/sdd-lite-diagram.md`](docs/sdd-lite-diagram.md) draws its steps, its stops, and when to pick it over `sdd-flow`.
- **`cross-cutting-adr`** — Captures cross-cutting architectural decisions as numbered ADRs under `SDD/adr/`. Triggers on comparison-with-selection patterns, explicit invocation, or ambient detection. Operationalizes Principle 3 (Living Documentation).
- **`improve-claude-md`** — Audits `CLAUDE.md`/`AGENTS.md` and `CLAUDE.local.md` to strip discoverable content and concentrate on preferences, behavioral nudges, and corrections. Mirrored from [pablooliva/claude-skills](https://github.com/pablooliva/claude-skills).
- **`ai-agent-security-review`** — Adversarial security review of **agentic** systems against the OWASP AI Agent Security Cheat Sheet (tool least-privilege, prompt-injection defense, memory/context security, human-in-the-loop for high-impact actions, output guardrails, monitoring, multi-agent trust, data protection, adversarial validation). Runs standalone on a spec, research doc, diff, or codebase; the same vendored control catalog (`skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`) is what `sdd-flow` consumes at its three gated hook points. Distinct from classical appsec, which stays with the `security` panel value and `/critical-review`.
- **`bb-worktree-init`** — One-time, per repo: makes a new or existing project ready for BB IDE worktrees. Inspects untracked config, env keys (names and value shapes only — never values), lockfiles, and local databases; proposes a plan for approval; renders bundled templates into `.worktreeinclude`, `.env-setup.sh`, a `.bb-env-setup.sh` symlink, and (only when needed) `.bb-env-teardown.sh`; then validates statically and, on approval, in a throwaway worktree. In a repo that already has the files it proposes edits instead. Does not commit.
- **`observability-init`** — One-time, per application: installs the tracing foundation, so every request leaves a record of what it called. Inspects the repository (framework, entry points, model and external calls, where configuration is loaded, how the tests build the app, the application's own rules about what may be recorded); proposes a plan for approval; renders bundled templates into one bootstrap module (the only file of the application's own code that names a tracing backend; the trace lookup reads the backend's address to read traces back), a wrapper for entry points the framework does not see, a test that fails when an entry point is not traced, a trace run that writes every span to a local file, a trace lookup that finds a real request's trace in Opik and prints it as a call tree (3.13.0), and `SDD/OBSERVABILITY.md`. Then proves it on the application: a real trace is read back from the backend and the trace lookup prints it, the kill switch stops everything, the entry-point test fails when tracing is taken off one entry point. Uses OpenTelemetry, so traces go to Opik or Langfuse by changing two environment variables. The rules it applies — what gets a span, what is never recorded, the switches — live in `skills/observability-init/references/tracing.md`. Python applications only for now. From 3.8.0 the bootstrap module also records every call to the application's own functions, with no change to them (Python 3.12 or later), and leaves their arguments and results out unless one setting asks for them — or, from 3.13.0, unless the call failed: then its arguments are recorded, with a switch to turn that off. Run it when no `/sdd-flow` cycle is in progress; from 3.8.0 `sdd-flow` uses the foundation in every later cycle. Never prints env values, never writes a credential, does not commit.
- **`eval-harvest`** — After a shipped tier has been used: turns the answers you marked wrong in Opik into proposed eval cases for the next tier. Lists the marked traces through the application's trace lookup; for each one you pick, drafts an invented case that should fail the same way (the real text stays in Opik) and checks a rule-based case against its own bad and good example; writes the ones you approve to `SDD/flow/HARVEST-[name]-[date].md` and one line in the tier plan's `## Feedback`. The next `sdd-flow` cycle's design brief adopts, defers, or drops each case. Makes no model call, writes no eval file, edits no code, does not commit. Opik and Python applications with the tracing foundation only.
- **`worktree-merge`** — Lands the committed work of a git worktree on the main line. Works on any linked worktree and is adapted to BB IDE: it resolves the target branch (BB's recorded default branch, else the remote's), syncs the work branch with it *inside the worktree* so conflicts never reach the main checkout, verifies, then fast-forwards the target — or opens a pull request when asked. In a repo with an `SDD/` folder it detects ADR and feature numbers that both this branch and the target claimed, and renumbers this branch's side after you approve the old → new mapping. Before the worktree goes away it surfaces git-ignored files that exist only there, and never copies a script-rewritten env back into main. BB-managed worktrees are left for BB to remove when the thread is archived (with an offer to sweep already-merged `bb/*` branches); other worktrees are removed with their branch, on confirmation.
- **`prompt-doctor`** — Diagnoses a task prompt *before* you send it to an agent, against a ten-component anatomy (grounding link, stakes, priorities, ranked priorities, hard constraints, marked-negotiable opinion, knowledge-gap disclosure, the one clear ask, early-exit permission, precise done-condition). Grades each Present/Weak/Missing/N-A with quoted evidence, names what each gap lets the model decide for itself, and asks you for the facts only you hold. Never executes the prompt under review and never invents stakes or constraints; the rewrite is opt-in and keeps unanswered slots as visible placeholders. Anatomy from Theo (T3.gg) plus Goedecke's ranked priorities and hard constraints.
- **`rephrase`** — Restates the report at the end of a piece of work (a delivered solution, a finished phase, a whole cycle) as four short sections in a fixed order: Done, Pending, Blocking, Next. Drops process narration, restated requests, settled reasoning, and file-by-file tours. Adds no facts and does no new work — it never re-runs tests or re-reads code, unverified work is reported as unverified, and failures and skipped steps always survive. An empty section reads `None`. Invoke with `/rephrase` (bare, a file path, or pasted text) or by asking "rephrase that".
- **`simplicity-challenge`** — Challenges a proposal, plan, design brief, or spec for doing or building too much, *before* it is implemented. Works on two axes — what it does, and how it is built — and reports the smallest version still worth using, a table of cuts (cut, or defer to Tier 2 / Tier 3) with what each one loses and what it would cost to add later, and what it kept because it is unsafe to leave out. It only removes or defers: it never adds requirements, never edits the target, never implements. On request it rewrites the proposal in reduced form or writes a tier plan. The tier standard it applies — three tiers (POC-plus, Standard, Full), two tenets (scope never rigour; nothing is built ahead), the floor, and the cut tests — lives in `skills/simplicity-challenge/references/tiers.md`. Runs only when asked: `/simplicity-challenge [file path | last] [functional | structural]`, or an explicit request such as "is this over-engineered?", "what's the simplest version?", "what can we defer?", or "tier this" — never just because a proposal appears. Complements `/critical-review`, which argues a proposal is not enough; not for code already written (the built-in `/simplify`).
- **`worth-building`** — Asks whether a proposed piece of work should be built as planned at all, *before* or early in building it. Puts six questions to a proposal, design brief, spec, or plan: the cheapest run that could kill the idea and whether it comes first; the best the idea can do and whether something simpler gets most of it; the size of the change against everything built around it; what a user sees after each stage; which safeguards need code and which need one written rule; and the budget with the point at which to stop and re-plan. Reports one page — a verdict (proceed, reorder, shrink, or stop), the kill test spelled out, the budget, and the tripwire. `recheck` runs it again after the first slice, with measured cost in place of the estimate. Run it before `simplicity-challenge`: there is no point trimming a plan that should be reordered or stopped.
- **`improve-codebase-architecture`** — Surveys *existing* code for deepening opportunities: shallow modules that could become deep ones. Biases the scan toward recently changed files (or the area or spec you name), keeps only candidates that pass the deletion test, writes a visual before/after HTML report to the OS temp directory, then interviews you through the one candidate you pick and ends with a decision summary to hand to `/sdd-flow`. Never edits code or writes into the repo. User-invoked only (`/improve-codebase-architecture [area | spec path] [report only]`). Uses the same depth standard as `sdd-flow`'s module-depth specialist, so a spec review and a code survey mean the same thing by "shallow". Adapted from [mattpocock/skills](https://github.com/mattpocock/skills).
- **`retro`** — Retrospective on a development cycle that proposes changes to the agent's *environment* — automated checks, review standards, steering files, tooling, information access — rather than to the code. Reads the whole cycle, not just the current session: `scripts/session-digest.py` lists every session of the repository across its worktrees and reduces each (and its subagents) to prompts, failed calls, long lookup runs, repeats, and oversized results, with transcript line numbers; `references/sdd-evidence.md` maps the `SDD/` records an `sdd-flow` run leaves behind. Proposes only. User-invoked only (`/retro [feature | branch | since <date> | session <id>]`). Distinct from `sdd-flow`'s per-slice retrospective, which records lessons about the feature. Adapted from [mattpocock/skills](https://github.com/mattpocock/skills).

### Commands

These are **interactive commands you run yourself** (depth 0, so they may delegate to subagents):

- **`/adr-capture`** — Manual entry point for the `cross-cutting-adr` skill.
- **`/prompt-doctor`** — Manual entry point for the `prompt-doctor` skill. Takes a pasted prompt, a file path, or the last draft in the conversation.
- **`/research-clarify`** — Structured interview that externalizes your design concept before any codebase research. Satisfies the `sdd-flow` Step 1.5 clarification gate. On a next-tier cycle it interviews for feedback on the tier already shipped instead.
- **`/critical-review`** — Standalone adversarial review of a research doc, spec, or implementation.
- **`/continue`** — Resume a session after any of the four compact commands below: loads the compaction file that `progress.md` names (under `SDD/orchestration/compacted/`), or the one whose path you pass, and continues from its `## Continuation Priorities`.
- **`/adhoc-compact`** — Generic mid-phase compaction, for ad-hoc or follow-up work. Detects an active SDD phase and redirects to the phase-specific command below.
- **`/research-compact`**, **`/planning-compact`**, **`/implementation-compact`** — Phase-specific compaction. Thin wrappers that read `sdd-flow`'s own compaction bodies (`skills/sdd-flow/bodies/<phase>-compact.md`) and run them interactively, so a manual compaction produces the same artifact an orchestrated run would — no second copy of the templates to drift.
- **`/commit`** — Commit conventions (no co-author attribution), including atomic per-slice commits.

## Keeping the work small

Three tools question a proposal before it is built, each from a different side. All three read a proposal, plan, design brief, or spec; none edits it or implements anything; each runs only when you ask. Run them in this order:

1. **`/worth-building`** — should this be built as planned at all? Its verdict is proceed, reorder, shrink, or stop. Run it first: there is no point trimming a plan that should be reordered or stopped. A *shrink* verdict points to the next step.
2. **`/simplicity-challenge`** — the work is worth doing; what is the smallest version still worth using? It cuts or defers item by item, on what the proposal does and on how it is built, and keeps the floor (data safety, security, loud failure) on purpose.
3. **`/critical-review`** — argues the opposite case: what is missing or wrong. Run it on the reduced version, so the gaps it finds are gaps in what will really be built.

In `sdd-flow` the natural moment is the design gate, before you approve the brief — the last point before a spec is written. The flow reminds you of `worth-building` there and after a plan's first slice (`/worth-building recheck`, with the measured cost in place of the estimate); it runs none of the three itself.

For code that already exists, use something else: the built-in `/simplify` cleans up a diff, and `improve-codebase-architecture` finds shallow modules in a codebase.

## Coexisting with the SDD plugin

The SDD plugin is **optional and uninstallable** — `sdd-flow` does not need it. If you keep both installed:

- **Command-name disambiguation.** Several command names exist in both plugins (`/critical-review`, `/continue`, `/commit`, `/adhoc-compact`, `/research-clarify`, `/research-compact`, `/planning-compact`, `/implementation-compact`). Claude Code may require the `/agent-engineering:` prefix (e.g. `/agent-engineering:critical-review`) to pick this plugin's copy.
- **Duplicate transcript logs.** Both plugins register a `SubagentStop` hook pointing at their own `log_subagent_call.py`. With both installed, each subagent stop is logged twice — harmless, just duplicate transcript entries.

## Status

Version 4.2.0.

### What's new in 4.2.0

`sdd-flow`'s code reviews also judge fit and size. The code review, each slice review, and the adversarial review of
the code ask whether a change matches the code around it, reuses what exists, is as small as the tier allows, and sits
where the next person would look (`skills/sdd-flow/references/fit-lens.md`). A file changed outside the design brief's
footprint is a finding unless the spec records it as a departure. A finding that adds a file, a layer, or a duplicate
helper is MEDIUM, and is fixed by removing or merging code; each fix round reports its net line change. Evidence and
decision: `proposals/review-criteria-2026-11-12.md`.

### What's new in 4.1.0

`sdd-flow` no longer counts enforcement sites. The proof that every place in the code enforcing a rule is listed and
tested is replaced by one adversarial security check at the end of the feature, and LOW findings no longer cost review
rounds. Second part of `proposals/sdd-flow-simplification-2026-11-12.md`; the evidence is in
`proposals/enforcement-site-proof-2026-11-12.md`.

**Why.** On two applications the blind count and its diff did not converge on large features (5–8 rounds, halts the
owner had to end), produced mostly inventory rows and tests for places already guarded, and cost hours per round. What
it found that mattered were security gaps, found by a reader trying to break the code. Long review loops were also
driven by fixing every LOW finding.

- **Removed:** the blind site count (4a.5, and the count in 4e.5), `scripts/site-diff.py`, the control register in the
  spec, the filing conventions, the site inventory, the `SITE-COUNT-*`, `SITE-DIFF-*`, and `REVIEW-SITES-*` files,
  the `## Control Site Status` table, and the `## Awaiting Site-Count Resolution` stop. The tier no longer sets a proof
  depth.
- **New: the final check (4e.5, `bodies/final-check.md`), on Codex.** It reads every security rule of the spec — its
  `SEC-` requirements, any other requirement that states a security rule, and with `agent_security` on the OWASP abuse
  cases that apply — for a path on which the rule does not hold: respellings and aliases, error paths, unset settings,
  missing configuration, values echoed back. Each gap is fixed with a test that fails when the guard is removed. At most
  two fix rounds; what is left stops the flow (`## Awaiting Final Check Resolution`). The same review runs the whole
  suite, the last look at the tests, and — with their gates on — the trace check and the eval check, as 4e.5 did.
  Standard: `references/security-verification.md`, which replaces `references/enforcement-sites.md`.
- **Implementers prove the security rules.** Each guard gets a test that fails without it, recorded under
  `## Security Proofs` in the implementation plan. Every other rule is held by an ordinary real test, checked by the
  Test Integrity Lens.
- **LOW findings are listed, not fixed.** In every review a pass is no HIGH and no MEDIUM. LOW findings go into the
  review's `LOW Findings (listed, not fixed)` section; you see them at the slice pause and in the end report.
- **Mutations run in a scratch copy.** A test is proven by breaking code in a copy of the working tree outside the
  repository (`python3 scripts/snapshot.py scratch` — uncommitted, untracked, and git-ignored files included), never in
  the working tree, so a mutation run cannot write into local databases or caches. A canary break checks first that the
  copy runs its own code (`references/test-integrity.md` §8).
- **Snapshots stay.** `scripts/snapshot.py` takes the fix-round snapshots a re-review reads; it replaces
  `site-diff.py --snapshot`.
- **Completion changes no code or test in any cycle**, not only with tracing or evals on: an item that needs either
  stops the flow at the final check's halt.

**Cycles in progress finish on the version that started them.** This version has no rule for the old site-count stop
or markers; a stop it does not recognise is shown to you and not passed.

### What's new in 4.0.0

`sdd-flow` has fewer modes, flags and stops. A stop exists only where you have something to decide or try; reading the
code is the reviews' job. This is the first of two releases from `proposals/sdd-flow-simplification-2026-11-12.md`.

- **One way to run.** Supervised and autonomous modes are gone, with the Step 1 mode question. The flow stops for the
  clarification question, the design gate, a spec that departs from the brief, a pause after each slice, an unresolved
  finding, and a sign-off.
- **The final commit no longer waits for a yes.** It stops only when a requirement waits for your sign-off (evals on).
  Otherwise the flow commits and ends with a short report: what shipped, what was deferred, anything left unproven, and
  the size of the diff.
- **Every slice ends in a pause for trying it.** The pause says what to run and what you should see (a new `Try it:`
  line on each slice in the spec), the slice's brief check, and the retrospective's re-plan advice when it has any. To
  re-plan, say so at the pause: the brief is revised, the design gate stops for you, and planning runs again. The
  re-planning stop is gone.
- **The clarification question is asked every time**, yes or no, unless a clarification document exists.
- **Codex is the only second model.** The reviewer can no longer be chosen; without the Codex CLI, or when a run fails
  twice, a Claude reviewer runs and you are told, as before. `SDD_FLOW_REVIEWER_ARGS` still passes arguments to Codex.
- **No meaningful slices → whole-feature, without a stop.** The planner sets `delivery_mode: whole-feature` with a
  one-line reason, and the flow tells you in its next message.
- **A missing OWASP catalog is a broken install** and halts, like the other shipped references; the agent-security
  checks are never switched off silently.
- **Tracing is settled at the design gate.** When the feature calls a model and the application has no
  `SDD/OBSERVABILITY.md`, the brief recommends running `/observability-init` before you approve; the flow looks again
  on approval, and the tracing and evals gates follow from that.
- **Removed flags are ignored with a one-line note** for this release, so old command lines keep working (the list is
  in `skills/sdd-flow/SKILL.md` → Arguments).
- **Finish a cycle in progress on the version that started it.** Nothing translates an older version's stop records;
  a stop this version does not recognise is shown to you and not passed.

### What's new in 3.16.1

- **`sdd-lite` reviews every change.** One Codex review and one check of its fixes now run on ordinary changes too, not
  only risky ones: an independent review is the check most likely to catch a bug, and the cap keeps it from growing the
  code. Without a Codex CLI it asks you before going on, for any change; the risk class stays in the brief so you see
  what a mistake would touch.
- **Its premise corrected.** The evaluation found `sdd-flow`'s correctness the same or better than plain's (never
  worse); what it cost was larger, broader code at 15 to 44 times the price. The skill, its diagram and this README now
  say that, instead of "without better code".

### What's new in 3.16.0

- **New skill: `sdd-lite`.** An evaluation of `sdd-flow` against plain Claude Code (four tasks, blind reviews by a second model) found the flow cost 15 to 44 times as much on clear tasks without better code, and a review of one project's later cycles found that what they reopened was small: the owner's decisions, the decision records, the glossary and the tier plan. `sdd-lite` keeps those and drops the rest: interview, one-page brief approved by you, build with tests in the main conversation, one Codex review only for risky changes, and a close-out of ADR, glossary and brief. It points you to `sdd-flow` when the work needs it.
- **A picture of it.** [`docs/sdd-lite-diagram.md`](docs/sdd-lite-diagram.md): which path to pick, the run step by step, and what it keeps and does not write.
- **Not yet exercised on a real cycle.** `sdd-flow` is unchanged.

### What's new in 3.15.0

A slice re-review after a fix round runs the tests the fix can affect, not the whole suite. In the eduKate project a review round went from about 30 minutes in October to between 2 and 11 hours, mostly from re-running a 44-minute traced suite before every re-review.

- **The tests the fix can affect.** A re-review whose fix round has both snapshots runs the test files the fix changed, the test files that reach a changed module (following imports, and fixtures, through other application modules), the slice's acceptance check, and the tests behind the previous review's findings. It runs the whole suite instead when the fix touches what decides how tests are collected or run (`conftest.py`, `pytest.ini`, a CI workflow and the like), or when it cannot tell which tests a change reaches. The `Re-review:` line names the tests run and their pass count.
- **The whole suite and the trace check at the end.** When the re-review would otherwise pass the slice, it runs the whole suite and the Tracing Lens before it writes its verdict; a test that fails there is a HIGH finding. While a re-review still has findings, the Tracing Lens waits — unless the previous review had a tracing finding, which it re-checks. A slice still leaves the loop only through a review that ran the whole suite.
- **The stall check sets aside what only the whole suite found.** That run writes `## Whole Suite SLICE-XXX iter N - w HIGH raised` directly before its review marker, and the stall check leaves those `w` HIGH out: they were hidden from the reviews before, so they say nothing about whether the fix loop is progressing. The 3-round cap is unchanged.

Unchanged: the eval run of record before every review, the first review of a slice (in full), and the whole-feature final check (4e.5), which runs the whole suite and the trace check in full.

**Runs already in a fix loop** take the new rule at their next re-review that has both snapshots; a run that began implementing before 3.14.0 takes no snapshots, so its re-reviews stay in full.

**Not yet exercised on a real cycle.** The rules were reviewed by Codex until it had no findings; no script changed.

### What's new in 3.14.4

- **An eval case names its spec.** A case's `requirement` in `evals/cases.jsonl` is now `SPEC-[###] REQ-XXX`. The file holds every spec's cases and requirement IDs restart in each spec, so in the trial a Tier 1 case's `REQ-002` showed up in Tier 2's results beside Tier 2's own `REQ-003`. Lines written earlier keep their bare IDs and are read as naming the spec that added them.
- **Implementation is split into chunks only when the change is wide.** The whole-feature flow split the work whenever the spec had more than 8 requirements and edge and failure cases; in the trial that made 4 chunks of a one-sentence prompt change. It now splits only when the approved brief also names more than 3 areas to change.

### What's new in 3.14.3

Two planning gaps found by the trial application's Tier 2 cycle.

- **The spec fix is checked.** After the spec's critical review, a fix step (3e) changes the spec, and until now nothing read those changes before they were committed — in the trial, a fix that resolved a HIGH finding went in unreviewed. A new step, 3e.5, has the cycle's reviewer check each HIGH and MEDIUM finding against the fix and read the changed passages for anything the fix broke. Anything still open gets one more fix and one more check; if it is still open then, the flow stops for you to fix the spec by hand.
- **A design brief never promises an acceptance with no judged eval.** In the trial the brief promised that the owner would read and accept the new hints, with no judged eval behind it; the spec review rated that HIGH only after the brief was approved, which forced the stop at the deviation check. The brief's rule now says what you read and accept always has a judged eval behind it, and a reading by hand with nothing scoring it is a manual check, not an acceptance.

### What's new in 3.14.2

Fixes to the review path, from the trial application's Tier 2 cycle, where both main reviews fell back from Codex to Claude.

- **Codex reviews run with network access.** In Codex's sandbox a test that opens a local port failed with "Operation not permitted" (37 of the trial's 261 tests), so the reviewer could not finish. The script now turns the sandbox's network access on; the reviewer's commands can then reach the network too.
- **No read limit on a second-model review.** The 15-read Safety-Net protects a Claude subagent's context; Codex manages its own, and the limit only cut each review into handoffs — eight in that cycle. A second-model prompt now carries no Safety-Net; Claude-route reviews keep it.
- **A failed review run is marked as failed.** A reviewer writes its verdict line while it runs, so a run that then fails could leave a "REJECTED" line that looked real. The orchestrator now appends `## Failed Review Run - …` after it.
- **`sdd-flow` names what it needs from bb.** It relies on Claude Code's built-in subagents; in bb the Claude Code provider setting `subagentsDisabled` must be `false`.

### What's new in 3.14.1

- **A next-tier cycle is no longer split before its design brief.** `/sdd-flow --next-tier` made the same scope check as a first cycle, on a task description that holds the most the tier could ever contain — its whole sketch and every deferred item aimed at it. On the trial application's Tier 2 that check split the tier into four separate features and stopped; the design brief, once the split was overridden, cut Tier 2 to one prompt sentence and one eval case. The split had sized work the brief was about to remove, and its items, run as plain `/sdd-flow` tasks, were no longer tied to the tier plan. A next-tier cycle now skips the scope check; its design brief makes the size check, moving what does not fit one cycle to a later tier — or, when no cut of the tier fits, saying so at the design gate, where you narrow what this cycle builds or stop.
- **The scope check never says the flow goes on after a split.** On that run the scope subagent wrote that the orchestrator would pick the first item, though a decomposition always stops the flow; its instructions now say so.

Splitting a tier into parts, each its own cycle, stays for later (`CLAUDEPLUG-13`, `proposals/tiers-in-parts-2026-10-18.md`).

### What's new in 3.14.0

Lighter `sdd-flow` reviews. Two trial cycles on a small application showed the weight: one stopped by hand after five hours of planning and three review rounds on its first slice; the other changed no application code beyond adding evals, yet its first code review rejected it with 24 HIGH findings and its final check took five rounds, three of them about `evals/run.py`, a file the plugin renders from its own template. Two changes:

- **A review after a fix round reads what the fix changed.** Before each fix and before each re-review, the orchestrator saves the working tree as a commit no branch points to (`scripts/snapshot.py`; the index, HEAD, and the stash are untouched). The re-review lists each finding of the review before it as closed or still open, and reads only the change; the trace and eval checks still run in full. The first round of the final check, and the first round after you resolve a stop, are reviewed in full. Slice review documents now carry their round in the name.
- **The plugin's own files are not re-proven.** `evals/run.py`, while it equals its template apart from its three placeholders, and the tracing files `/observability-init` rendered are tested where their templates are made; a review checks that `evals/run.py` still equals its template.

**Exercised once since (2026-10-18):** the trial application's Tier 2 ran on 3.14.0 — one round each for the code review and the final check, with no HIGH finding; no fix round ran, so the snapshots were not reached.

**Not in this release:** more than three tiers, or a tier delivered in parts (`CLAUDEPLUG-13`).

### What's new in 3.13.2

- **The trace lookup reads the trace-specific backend settings.** The bootstrap module sends traces where `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` and `OTEL_EXPORTER_OTLP_TRACES_HEADERS` say, when they are set, but the trace lookup read only the general `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS`. An application set up with only the trace-specific forms sent its traces, and the lookup then said no backend was set — or, with both forms set to different values, asked the wrong address or project. The lookup now reads the trace-specific form first, as the exporter does. An application installed earlier gets the fix when `/observability-init` is run on it again in audit mode, which compares `scripts/trace_lookup.py` with the current template and proposes the change.

### What's new in 3.13.1

- **The observability record names the span-file check as the skill's.** `/observability-init` runs `check-span-file.py` from its own directory, but nothing said how to name it in the record's "Shown to work" lines, and the trial application's record named it `scripts/check-span-file.py`, as if it were in the application. A later `/sdd-flow` cycle then looked for it there, recorded it as missing, and the owner was asked to add a script that was never meant to exist. The record now names it as the skill's script, and audit mode proposes rewording such a line in a record written earlier — it never adds the script to the application.

### What's new in 3.13.0

The fourth and last build step of the tracing-and-evals proposal (`proposals/observability-and-evals-2026-10-04.md`): what goes wrong in real use comes back into the next cycle. It was built ahead of using step 3 on a real cycle, by the owner's decision, so that the trial application's next round could take all of it at once.

- **The trace lookup.** `/observability-init` renders one more file into the application, `scripts/trace_lookup.py`. It lists the newest traces in Opik (`--failed`, `--marked` for those a person marked, `--at "<YYYY-MM-DD HH:MM>"`), and prints one trace as a call tree that ends with the call where the failure started. By default it prints no recorded text — names, files and lines, timings, error classes — but it does print the marks a person left, and a comment can quote what a user wrote; `--content` adds the recorded text for one trace, and `--model-call --out <file>` writes the model call to a file so it can be sent again. Opik only, through its REST API. One paragraph in the application's `CLAUDE.md` or `AGENTS.md` tells its coding agents to use it when a bug is reported. An application set up earlier gets it by running `/observability-init` again (audit mode), which proves it on a trace the backend already holds.
- **Values on failure.** When a call to the application's own functions ends in an exception, the arguments of each call the exception leaves are recorded as they stood — text cut at 200 characters, never a return value or the exception's text. It is on by default, off with `TRACE_FAILURE_VALUES=off`, and off by default in an application that takes requests and has no header reader. A user's question handed to the failing function can reach the backend: an application whose rules forbid that switches it off, and its record says so. Measured cost: about 3 microseconds more per request, 7 more per failed call. Audit mode asks about the application's rules before adding it.
- **The eval run reads the env file as the application does** — quotes, a ` #` comment, `export`, the first line of a name, the environment winning. Before, a secret written with a comment after it was not replaced in the results. An application that rendered `evals/run.py` from 3.12 renders it again: the review compares it with the template.
- **`/eval-harvest`** — a new skill, run after a shipped tier has been used. You mark the answers that were wrong in Opik — a score, a tag, or a comment. It lists the marked traces through the application's trace lookup, you pick the wrong answers, and for each it drafts an **invented** case that should fail the same way — hard where a rule can catch it, judged otherwise — and checks a hard case against its own bad and good example. You approve each case in full. Approved cases go to `SDD/flow/HARVEST-[name]-[date].md`, with one line in the tier plan's `## Feedback`. It makes no model call and commits nothing. The real request and answer stay in Opik: the skill reads them for the traces you pick, and writes them nowhere.
- **The next cycle settles each harvested case.** The flow offers its design brief every harvested case not yet adopted or dropped. The brief adopts each one, unless it **defers** it (its behaviour belongs to a later tier) or **drops** it (the brief changes the promise the case checks, and names that change in a Key decision you approve). In a cycle with evals off nothing is adopted: a case the brief adopts is recorded as not adopted and stays open. Tracking is per case, so a deferred case comes back to the next cycle while the rest of its file is adopted. An adopted case goes into the spec's `### Evals` under a requirement of that spec; the implementer runs it once before changing anything for it, and the completion announcement names any harvested case not seen to fail then — a hard case that passed, which may not reproduce what the person saw, or a judged case with its scores, or a run with no result.

**Where it differs from the proposal** (its "Step 4 as built"): the harvest proposes cases and never writes `evals/cases.jsonl` — a case no spec states would be run by every review, judged by none, and fail every unrelated feature's review until fixed; a harvested case is confirmed to fail in the next cycle, not at harvest, because the eval run cannot run one case; traces are read through a script and Opik's REST API, not its MCP server.

**Not exercised on a real application.** The trace lookup was run against the trial application's Opik (112 traces): listing, `--failed`, `--at`, and a failed trace's tree. No trace there was marked, so `--marked` has only been tested against a stand-in server, and `/eval-harvest` — instructions, with no script of its own — has never been run; values on failure has not met a real failure in the trial application; and no cycle has yet been offered a harvested case. Each part was reviewed by a second model (Codex); every finding was fixed, or declined with its reason in the commit message.

### What's new in 3.12.1

Two fixes to how `sdd-flow` hands an unfinished step to a successor, both present since handoffs existed. The first was found by the review of 3.12.0, the second by a question about the first.

- **A step that is handed off mid-way is told which step it was.** A subagent that has read too many files stops, writes a handoff note, and the flow starts a successor to finish its step. The successor's instruction file is a general one, and the rule that starts it did not say to pass the instruction file the first one was following, nor its mode, scope, and iteration. The successor of the final check, say, was not told that this was the review it was finishing, so it could leave out a check that review requires, or write the wrong marker. Now the first spawn's prompt is the rule: the successor is given that step's own body by path (as `STEP BODY`), its task and embedded rules, its mode, scope, iteration, and base commit, and every input and output. The continue body says how to pick the work up; the step's body says what must still be produced. The handoff note's entry in `progress.md` gains a `Step:` line, so a later session can do the same.
- **The successor is the same kind of agent as the one it replaces.** Every successor used to be the Sonnet workhorse. A critical review or a panel synthesis that Claude's Opus reviewer had begun was therefore finished on Sonnet, by an agent whose standing instructions tell it not to do adversarial review; a design brief begun on Opus was finished on Sonnet too. Now the successor is started as the agent type of the step's first spawn, with that spawn's model override. It costs more only where the step was on Opus already. A critical review on the second model was never affected: its continuation is a new call to the same reviewer, with the same role file.

A run handed off before 3.12.1 has no `Step:` line: a resumed session works the step out from where the note says the work stopped, and asks when that leaves two candidates. **Not exercised on a real cycle:** no handoff has been made under the new rule; the wording was reviewed by a second model.

### What's new in 3.12.0

Evals inside `sdd-flow` — the third of four build steps of the tracing-and-evals proposal (`proposals/observability-and-evals-2026-10-04.md`). A test checks what the code does with a model's answer, and gets that answer from a stand-in; nothing in a cycle looked at what the model really says. An eval puts a written example to the running application and checks what comes back. An application without the tracing foundation, and a feature with no model in it, are unaffected: the gate is off and the cycle runs as it did in 3.11.0.

- **Two kinds.** A *hard* eval applies a rule to the output — a phrase is there, a phrase is not, a field, a refusal — and blocks like a failing test. A *judged* eval is scored by a second model call and only informs: no score is ever compared with a threshold, because the same output can be scored differently twice. One definition: `skills/sdd-flow/references/evals.md`.
- **A second gate, settled with the first.** The spec gains `evals: auto | true | false`. At 3c it resolves to on with `true`, or with `auto` when the application has the tracing foundation and the spec has a model in it. One line records both gates: `## Gates - tracing: <on|off>, evals: <on|off>`. The stop for a gate that cannot be decided is now `## Awaiting Gate Decision`; a block under the old header is the same stop.
- **You decide how quality is judged, at the design gate.** The design brief gains one Key decision, `How answer quality is judged`: which behaviours a rule checks, and which are left for you to accept.
- **The cases are written in the spec, before any code.** `### Evals` under `## Validation Strategy`: each eval names one requirement and writes its cases out in full — an invented input, and what the output must and must not contain, or a rubric for the judge. Each slice names the evals it must pass. The spec's critical review checks that every requirement about what the model says has a hard eval, or is listed for you to accept and has a judged one. An implementer that wrote its own cases would write the ones its code passes.
- **The implementer builds them.** The first work with an eval renders the eval run from templates (`skills/sdd-flow/templates/evals/`, Python only, standard library only): `evals/run.py`, `evals/task.py` — which calls the application's own code, with the real model — `evals/cases.jsonl`, and a test of the checks. Every hard case carries an answer its check must reject and one it must accept, and the run calls no model until each check does both.
- **Every case is run three times.** A hard case passes only when its check holds on all three, so a behaviour the model shows only some of the time fails — as `unsteady`, told apart from `never passed`. In a trial on a scratch copy of the trial application, it stated a result it is meant to lead a student to in 2 answers of 7.
- **The flow makes the run a review reads.** Before each slice review, the code review, and each verification of the final check, the orchestrator runs the application's eval command and hands the review the results (`SDD/reviews/EVAL-RESULTS-*`). The review's Eval Check reads that run and the eval files against the spec, from a fixed list of fifteen findings — among them a hard case that failed, a case weakened or removed, a check that passed a bad answer, an application taught its cases, and an eval task that does not go through the application's own code. A reviewer never makes the run: a review on a second model may sit where no model can be reached.
- **Runs go to Opik,** one experiment per review, by plain HTTP requests — no SDK and no new dependency in the application. A failed upload is a warning; the results files in the repository are the record.
- **The last check comes after the last fix.** The final check (4e.5) puts every case to the application again before each of its verifications, and an eval finding counts toward its three-round cap and its stop. Completion reads the final results for the summary and changes no code or test.
- **A person accepts what only a judge can score.** A requirement no rule can check is a *sign-off requirement*. With one in the spec, the commit checkpoint (4h) stops for it — the one reason it stops: it shows each such requirement with its judged scores and the path to the outputs, and yes both commits and accepts. In per-slice mode each slice pause shows the last line of the slice's eval run.
- **One new stop:** `## Awaiting Eval Run`, when the application's model cannot be reached twice in a row before a review. Nothing is reviewed until it can be, and it costs no fix round. A run that reaches no model is "no result", never a list of failed cases.

**What it costs.** With the gate on, every review makes real model calls: every case the application holds — an earlier feature's included — three times, and twice that for a judged case, whose every answer is also scored. In the trial, five cases took about 20 seconds for one run of each.

**Where it differs from the proposal** is listed in the proposal's "Step 3 as built". The largest: the flow's main session, not the reviewer, makes the eval run; one stop was added; the templates live in `sdd-flow`, not `observability-init`; there is no eval library; and the eval run is separate from the trace run.

**Runs started before 3.12.0.** A cycle that passed 3c earlier has a gate line with no `evals:` part: evals stay off for it to its end.

**Not in this release:** `/eval-harvest` (build step 4, in 3.13.0), and templates for a language other than Python.

**Not yet exercised on a real cycle.** The eval run's templates have 56 tests against a stand-in task and a stand-in for Opik. They were run once against a real model on a scratch copy of the trial application — four hard cases passed all three runs, one judged case was scored, the run was sent to Opik and read back. The record is `proposals/observability-and-evals-trial-2026-10-12.md` (counts, verdicts, and scores; the raw results were not copied into this repository). That run was before the review fixes to the runner, so it was made once more with the runner as released (2026-10-13): the same five cases, the same result, sent to Opik and read back. Every case passed in both, so nothing on the failing side — a hard case that fails, an unreachable model, a secret in an output — has met a real model. No cycle has yet planned an eval, built one, had one reviewed, or stopped for a sign-off: everything the flow does with evals rests on the review of its wording until the trial application's next cycle.

### What's new in 3.10.1

- **`sdd-flow` reminds you of `worth-building` at the two moments it is useful.** The design gate's message gains one line, before the reply instructions: `/worth-building` on the brief asks whether this should be built as planned at all. The pause after a plan's first slice gains one line: `/worth-building recheck`, with the number of review rounds that slice took. Both are reminders only — the flow never runs the skill, never waits for it, and records nothing about it. Its verdict reaches the flow as your reply at the gate, or as your decision at the pause.

### What's new in 3.10.0

- **New skill: `worth-building`.** Everything else that reviews a plan asks whether it is correct, complete, or too large. Nothing asked whether the work should be done in this order, or at all. The skill came out of a cycle that built seven slices of measurement tooling before running the one forty-minute test of the idea the tooling was for; the test showed the idea did not work. `worth-building` asks six questions of a plan and gives one verdict — proceed, reorder, shrink, or stop — with the kill test spelled out, a budget, and a tripwire: an observable condition at which to stop and look again.
- **Two moments to run it.** At a design gate, where cost is an estimate; and with `recheck` after the first slice or milestone, where it is a measurement. On a recheck it separates the two causes of cost — the number of things being built, and the rounds each one takes — because they need different answers: the first is shrunk, the second is a process to lighten.
- **Where it sits.** Before `simplicity-challenge` (which trims a plan it accepts as worth doing) and before `/critical-review` (which looks for what is missing, and so tends to add). It is user-invoked. (From 3.10.1 `sdd-flow` reminds you of it at the design gate and after the first slice; it still never runs it.)

### What's new in 3.9.0

Two changes to how `sdd-flow` reviews, both aimed at the same weakness: everything a cycle produces was written by Claude, and was then reviewed by Claude against a green test run.

- **Reviews are run by a second model family.** The research, spec, and implementation critical reviews, the code review, each slice review, and the final check are given to a different model through its command-line agent: the Codex CLI. The second model is given exactly the prompt the Claude reviewer would get, after a fixed preamble; it reads the same body by path and writes the same review document and marker, so nothing downstream changes. The reviewer is settled once at Step 0 and recorded. One definition: `skills/sdd-flow/references/second-model-review.md`; one script: `scripts/second-model-review.py`.
- **The fallback is marked, and never stops a cycle.** With no second model on the machine — or when a second-model run fails twice, including because the session's sandbox did not let the CLI start — the review runs on the Claude subagent it used before, and the line saying so goes to `progress.md` and to you. Every review document now carries a `Reviewed by:` line.
- **A review changes no code, and the script enforces it.** Before a second-model run the script records the working tree; afterwards it puts back any file outside `SDD/` the reviewer left changed — a mutation made in the working tree and not restored, say — and names it.
- **Test Integrity Lens.** Reviews used to ask whether tests exist, map to requirements, and pass. They now also ask whether the tests are real and whether anything was bent to get the green run. `skills/sdd-flow/references/test-integrity.md` states what a real test is — expected value from the spec, fails when the behaviour is broken, runs the code that holds the logic, checks an outcome the spec names — and seven checks: existing tests weakened or removed, anything kept out of the run, expected values copied from the code, tests that cannot fail (the reviewer breaks the requirement's code and runs its tests), stand-ins replacing the application's own logic, code fitted to the tests' inputs (the reviewer runs an input no test uses), and tests that do not prove what their name claims. The code review and every slice review run it in full, sampled by module risk; the implementation critical review runs it by reading, looking hardest at tests a fix changed; and the final check (4e.5), which now runs in every cycle, reads the tests once more after the last fix round — the first two checks, and for the tests the feature added, whether each expected value is still the spec's and each assertion can still fail. A HIGH finding rejects. Implementers and fix subagents are held to the same standard up front, and a pre-existing test may change only with a line under `### Test Changes` in the implementation plan naming the requirement that demands it.

The specialist panel stays on Claude subagents — up to eight reviews a round would be a great many second-model runs, and the spec critical review that follows it is on the second model. A cycle started before 3.9.0 finishes with the reviewers it began with. **Not yet exercised on a real cycle:** the script is unit-tested against stand-in CLIs and was run once against the real Codex CLI on a scratch repository — it wrote its review file, and the script put back the source file it had been told to leave changed. No full cycle has used the new routing or the Test Integrity Lens yet.

### What's new in 3.8.1

One fix to `observability-init`, found the first time 3.8.0 was applied to a real application (the trial application, by running the skill on it again in audit mode).

- **A failure inside the function-recording hook no longer logs the exception's text.** When the hook itself fails, the bootstrap module logs one warning per process. In 3.8.0 that warning carried a full traceback, exception text included — and an exception's text can repeat what a user sent, which is why the tracing standard keeps it off spans. The warning now carries the exception's class name when it is one of Python's own, and line numbers of the bootstrap module — nothing the application or a request could have written — and the standard states the rule for the log line too.

An application already updated to 3.8.0 gets this by running `/observability-init` again: audit mode proposes the one edit.

That audit run is also the first time the function-recording hook ran on a real application, as that thread reports it: the application's tests pass, one real request's trace arrived in Opik with the model call beneath the function that made it, the kill switch stopped everything, and no value was recorded with the values switch unset.

### What's new in 3.8.0

Tracing inside `sdd-flow` — the second of four build steps of the tracing-and-evals proposal (`proposals/observability-and-evals-2026-10-04.md`). In an application that has the tracing foundation, a cycle now plans which calls a feature makes and checks that plan against what a real run recorded. An application without the foundation is unaffected: the gate is off and the cycle runs as it did in 3.7.2.

- **One gate, settled once per cycle.** Step 0 records whether `SDD/OBSERVABILITY.md` exists. The spec gains `tracing: auto | true | false`; at 3c the orchestrator turns that and the Step 0 record into `## Gates - tracing: on|off` in `progress.md`, and every later spawn is passed that line. `tracing: true` with no foundation, or an invalid value, stops planning with `## Awaiting Tracing Decision`.
- **The spec plans the calls.** With the gate on, `## Modules` gains `### Planned call graph`: one tree per entry point, with entry points, model calls (each with a maximum number of calls per request), and calls to other systems marked. Each slice names the marked nodes it builds. The spec's critical review checks the graph.
- **The implementer follows the tracing standard** for what it adds, and checks its marked nodes against the application's trace run. A difference from the plan is recorded as a deviation; the plan is never edited to match.
- **Reviews compare the plan with a real run — the Tracing Lens.** Defined once in `skills/sdd-flow/references/tracing-lens.md` and run by the slice review, the whole-feature code review, and the final check. The reviewer runs the trace run, renders its span file with the new `skills/sdd-flow/scripts/trace-tree.py` into `SDD/reviews/TRACE-TREE-*`, and compares the tree with the marked nodes in scope. Findings come from a fixed table: a header or secret on a span, more model calls in one request than planned, or a trace run that cannot be read (HIGH); a call the plan does not show, a marked node the run does not show, an entry point not traced (MEDIUM); three kinds of misuse of the tracing API in the application's own code (LOW). A model call is matched by the function that made it; where the tree cannot tell two nodes apart the review says so instead of passing them.
- **The last check comes after the last fix.** With the gate on, the final check (4e.5) always runs and repeats the comparison for the whole feature. Completion reads the final tree for the summary's `## Monitoring & Observability` and changes no code or test; if it finds something that needs either, the flow stops on the final check's halt and re-runs the final check after you resume.
- **The tracing rules are not a feature's security rules** unless a spec restates one with a `SEC-` ID.
- **`trace-tree.py`** turns a span file into a document: requests grouped by entry point, the fewest and most model and external calls in one request, each distinct tree of calls drawn once (at most ten per entry point), and a scan for headers and secret values. It prints names and counts, never recorded text.

Two additions to `observability-init` and the tracing standard, made in this release because the trace check needed them:

- **Every call to the application's own functions is recorded automatically.** The bootstrap module switches on Python's call-monitoring hook (`sys.monitoring`, Python 3.12 or later) for the application's own directories: each call gets a span named `<module>.<function>` with its file and line, and nothing in the application's functions changes. Libraries and the framework are left out. On an older Python no function spans are written, and the observability record says so.
- **Values are off unless asked for.** A function's arguments and result are not recorded. `TRACE_FUNCTION_VALUES=all`, or a list of module names, records them, cut to size; a parameter named like a secret or a header is never recorded, and recorded text is checked against request headers and secret-named environment values. With the setting on, that check is as good as its matching — the standard lists what it misses.
- **A cap on repeats.** After ten calls of one function from one caller, further calls get no span; the caller's span counts them (`calls.<function>.not_recorded`) and how many of those ended in an exception (`calls.<function>.not_recorded_failed`).
- **What it costs.** Measured on the trial application against a local stand-in for the model (a request of about 1.2 ms): 34 records per request instead of 5, and a median request about 0.5 ms (42%) slower. The cost is a fixed amount per call, so against a real model call of tens of milliseconds it is a few percent. The kill switch removes all of it.

Not in this release: evals (build step 3) and `/eval-harvest` (step 4). The design brief does not mention tracing yet. An application set up with 3.7.x keeps working; it gets function recording only when `/observability-init` is run on it again in audit mode. No feature had been built end to end with this release when it shipped; the trial application's next piece has been since (2026-10-09 to 2026-10-12, the trace check run in all twenty completed flow reviews, no gap found — see the proposal's "Step 2 as built").

### What's new in 3.7.2

Four fixes to `observability-init`, each found on its first run on a real application (a FastAPI app started with `fastapi dev`), where each had to be worked around by hand.

- **The last traces before a stop are no longer lost.** A server worker started by a reloader or a process manager is ended without Python's exit hooks, so spans from its last seconds were never sent: three requests made just before a stop left no trace. The bootstrap module gains `flush_tracing()`, called when the application shuts down; the tracing standard now makes that part of the bootstrap module's job.
- **The span-file check no longer flags the project name.** `check-span-file.py` treated every header in `OTEL_EXPORTER_OTLP_HEADERS` as a secret, so the Opik recipe's own `projectName=<application>` line — the same text as the service name on every trace — failed the check on every install. Only a header that carries a credential (an authorization header, a key, a token, a cookie) is a secret now, and the standard says so.
- **Discovery looks for tests that would send traces.** A test that starts the application from the repository reads the developer's real env file and would send traces on every run once backend lines are in it. A test that starts a real server with an environment of its own drops the trace run's variable, so its requests were missing from the trace run's file. The skill now searches for both, puts each in the plan, and the recipes say how to fix each.
- **The plan says everything that is recorded.** It now also states that a request's query string is recorded, and that a failed call records its error text, which can repeat what the other system answered. The standard's capture policy lists both.

The skill has now been run on the trial application itself (2026-10-07), with every proof seen except the swap to a second backend, which is deferred.

### What's new in 3.7.1

- **`observability-init`: sending to a second backend is no longer a condition for the foundation to count as installed.** Applications send to one backend (Opik here). In 3.7.0 the tracing standard also required showing that the same application could send to the other backend after changing only its two backend variables. That test is now run the first time an application needs a second backend; until then the skill reports it as not run and the application's observability record says so. Nothing else in the skill, the templates, or the standard changed.

### What's new in 3.7.0

- **New skill: `observability-init`.** The first of four build steps of the tracing-and-evals proposal (`proposals/observability-and-evals-2026-10-04.md` at the repository root). Run once per application, outside any `/sdd-flow` cycle, it installs a tracing foundation: one bootstrap module, a wrapper for entry points the framework does not see, an entry-point test, a trace run, and `SDD/OBSERVABILITY.md`. It then proves the result on the application itself, and reports any check it could not run as not run.
- **One tracing standard.** `skills/observability-init/references/tracing.md` defines what gets a span (every entry point, every model call, every call to another system — nothing else), what is recorded and what never is (headers; the value of a secret-named environment variable), the attribute rules, what makes a trace usable for evals later, and the switches. The switches are standard OpenTelemetry environment variables: off entirely, keep spans but drop model text, record a fraction, choose the backend. With no backend address set, nothing is sent.
- **Python templates only.** Proven on a FastAPI application that calls a model through the `openai` SDK, sending to Opik: the trace arrived with the route as its first span and the model call beneath it, with model, token counts, and messages recognised. Sending to Langfuse is not yet proven. Other frameworks and libraries have recipes marked unproven, which the skill's own proof step has to pass before it may call them done.
- **`sdd-flow` is unchanged.** It does not read the standard or the record yet; tracing inside a cycle is the next build step. `docs/observability-diagram.md` says which parts of the picture exist.

### What's new in 3.5.2

- **Research-stage ADRs wait for the design gate.** They are listed there and written on `approve`; a bare `approve` accepts all of them, and any can be dropped by title.

### What's new in 3.5.1

A review of `sdd-flow` as a whole (`proposals/sdd-flow-review-findings-2026-10-03.md`; fix plan beside it) found that the main path held together and the gaps clustered in three places: resuming after a stop, the per-slice path, and instruction files forked from hand-run commands that still behaved like them. No flow was run end to end for the review — every finding is a contradiction between two pieces of text. `SKILL.md` now states one rule per cause, and later edits are checked against them.

- **Bodies take their inputs from the prompt and nothing else.** A body no longer lists a folder to find its spec, research document, plan, or compaction file, so a second feature or tier in the repo no longer stops the slice path or the second implementation chunk. A body never commits and never resets `progress.md`; one that cannot proceed returns a failure instead of writing a stop note.
- **Only the orchestrator declares a phase done.** New markers `## Research - Accepted`, `## Implementation - Committed`, and `## Feature - Done` join `## Planning - Accepted`. A session that ended at the "ready to commit?" checkpoint no longer resumes as finished with nothing committed.
- **Resume reads the current feature only.** Step 0 opens each feature's record with `## Flow Started - …`; a finished feature is rotated to one `Finished:` line that no rule matches.
- **Every stop that waits for an answer is recorded and resumable.** A stop writes its block to `progress.md` before it asks, has a resume rule, and has a row in the diagram. A stop record the current version does not recognise is shown as written, never guessed past.
- **Research-stage ADRs are proposed, then written on approval.** Candidates are listed at the design gate and can be dropped by title; the separate confirmation step, which never completed, is gone.
- **Every slice state change, stop, and commit has a named owner.** The orchestrator marks a slice `Complete` and commits it, in that order, then writes `## Slice SLICE-XXX - Committed`. A slice whose fix loop reaches its cap stops with `## Awaiting Slice Resolution`, and `continue` re-reviews it from a fresh round.
- **A re-plan no longer collides with the plan it replaces.** The old plan's slice retrospectives and reviews move to `SDD/implementation/slices/superseded/<timestamp>/` — kept, not deleted — and resume, fix-round caps, and the learnings ledger read only the new plan's.
- **Removed: re-starting a finished slice.** The `--force` flag on slice start, `--confirm-restart`, and `## Awaiting Re-start Decision` were half-built and had no user-facing entry point. Change a finished slice in a later slice, or re-plan.
- **Panel values without a shipped specialist** (`accessibility`, `privacy`, `cost`) run on the general worker with the panel body instead of naming an agent that does not exist.
- **The compact commands and `/continue` follow one contract.** All four compact commands write under `SDD/orchestration/compacted/`, record the file's full path in `progress.md` (or, with `/adhoc-compact`'s Skip option, hand you the path to pass to `/continue`), carry the same `## Continuation Priorities` section, and leave a pending `## Awaiting …` block as the latest block so a stopped flow is still found (unless you tell `/adhoc-compact` to set the whole file aside). `/continue` loads the file `progress.md` names (it used to look in the wrong folder) or a path you give it, stops rather than substituting when that file is missing, asks when several unrecorded files exist, gains a branch for generic compactions, and points at `/sdd-flow continue` when a flow is stopped waiting for an answer. Run it as `/agent-engineering:continue` when the `sdd` plugin is also installed. `/adhoc-compact` no longer offers to overwrite `progress.md` — it can set the whole file aside in `progress-archive/` instead, and asks first when that file holds an unfinished feature — and `/implementation-compact` no longer commits during a flow.
- **Runs started on 3.5.0 keep resuming.** Each new marker has a stated reading for a run that never wrote it.
- **Legacy-layout message corrected.** It named a `/sdd-migrate-layout` command this plugin does not ship; it now points at the `sdd` plugin's.

### What's new in 3.5.0

- **Tiers are mirrored to BB tasks.** The tier plan file stays the record; `sdd-flow` now keeps a parent task for the feature and one sub-task per tier in step with it, so a waiting tier shows on the board and you can leave feedback on it between cycles. On design-gate approval the approved tier (with any lower tier not yet shipped) goes to in progress and the rest to backlog, with the brief attached and, inside a BB thread, the thread too; before the final commit it goes to in review; at completion it goes to done with one comment saying what shipped and what to look at. `/sdd-flow --next-tier` copies the comments left on the next tier's sub-task into the tier plan's `## Feedback` before the feedback interview.
- **The tracker project is created when there is none.** A BB project with no linked tracker project gets one, named after it and linked to it — a missing project is not a reason to skip.
- **Never skipped silently.** Outside BB (no `bb` CLI, or a checkout that is not a BB project) there is nothing to mirror to: the flow says so in its next message and carries on. A failed `bb` command is retried once, then reported the same way; the tier plan is unaffected and the next mirror point tries again. The mirror never halts the flow.
- **A script, with tests.** `skills/sdd-flow/scripts/tier-mirror.py` (stdlib only; talks to BB through the `bb` CLI) does the work, so the orchestrator runs one command per mirror point. It only creates what is missing, so it is safe to repeat. 23 cases in `scripts/tests/test_tier_mirror.py` against a stub `bb`.
- **`/critical-review` checks the numbers.** The interactive command gains the feasibility-arithmetic check the flow has had since 2.3.0, in a general form: for any target that states quantities, it tests whether the stated goals fit inside the stated limits, and a failure is an automatic hold. It also points to `/simplicity-challenge` when a proposal looks over-built, rather than listing cuts itself. It stays independent of `sdd-flow`: it does not compare a spec against a design brief.
- **Workflow diagram.** New `docs/sdd-flow-diagram.md`: the whole cycle, the per-slice loop, and tiers across cycles as diagrams, with a table of what each stage does and where it can stop.
- This is step 3 of the build order in `proposals/tiered-delivery-2026-10-02.md` (§4). Step 4, the re-review of the flow, is not done.

### What's new in 3.4.0

Two linked changes to `sdd-flow`, aimed at one problem: the volume of what an agent proposes outruns the human's ability to review it, and approval becomes a reflex. Design and rationale: `proposals/design-brief-gate-2026-10-02.md` and `proposals/tiered-delivery-2026-10-02.md`.

- **Design gate (new Step 2.5).** The flow used to pause after research with a summary of findings and "Proceed to planning? (y/n)" — a decision without the material to make it — and then had no human pause anywhere in planning. That pause (Step 2f) is removed. In its place a subagent on Opus writes a design brief (`SDD/requirements/DESIGN-[###]-[feature-name].md`, new body `bodies/design-brief.md`) and the flow stops. The stop fires every time the brief is written or rewritten, and no flag skips it. You answer its questions, ask for changes (a revision round, as many as you want), or approve; `approve` is refused while a question is open.
- **The spec is held to the brief.** The spec gains `## Deviations from Design Brief`. Planning, the panel fix loop, and the combined fix must record every departure from the brief's decisions, exclusions, and answered questions; the spec critical review has a Design Brief Fidelity block (an unrecorded departure is HIGH); and Step 3g stops when any deviation is recorded, before a line of code is written.
- **Brief check on every code review.** The slice review and the whole-feature code review write a `## Design Brief Check` section: which outline entry was delivered, and which changed files fall outside the approved footprint. It is quoted at each slice pause, at the pre-commit checkpoint, and in the completion announcement. Information only — it never blocks a slice.
- **Tiered delivery.** The brief carries a `## Tiers` section and the gate a tiers line; reply `tier 2` or `tier 3` to build more, or pass `--tier N`. The spec gains `tier:` frontmatter and `## Deferred to Later Tiers` (`DEFER-XXX` rows, behaviour only). Deferred items are not requirements, so every existing "each REQ / each EDGE" rule keeps working; a deferred case the tier can reach gets a `FAIL-XXX` for its loud failure. A spec with no `tier:` behaves exactly as before.
- **Reviews respect the tier.** Panel specialists, the critical review, the code review, and the slice review do not flag what is on the deferred list; they do flag, at HIGH, a deferral that breaches the tier standard's floor, and they flag anything built ahead for a later tier. Spec fix subagents may resolve a finding about *absent* scope by deferring it; a finding about behaviour the tier builds is always fixed.
- **Tier plan and next tier.** `SDD/flow/TIERS-[feature-name].md` records what shipped, what was deferred, sketches of the later tiers, and feedback. The brief subagent writes it; the completion subagent updates it. `/sdd-flow --next-tier <feature>` starts the next tier as a new cycle: `/research-clarify` becomes a feedback interview, research is a delta on the previous tier's, and the brief opens with what was learned.
- **Not in 3.4.0.** Mirroring tiers to BB tasks (added in 3.5.0) and the re-review of the flow with current models — steps 3 and 4 of the build order in the tiered-delivery proposal.

### What's new in 3.3.0

- **New skill: `simplicity-challenge`.** Everything else in the plugin that reviews a proposal asks what is missing; nothing asked what is unnecessary. This skill argues that a proposal is too much. It states the need the proposal serves, runs each thing it does through four functional cut tests (evidence, by hand, hard-code, add-later cost) and each part it adds through four structural ones (existing code, moving parts, two adapters, later tier), and reports the smallest useful version with a table of cuts and their costs.
- **One tier standard.** `skills/simplicity-challenge/references/tiers.md` defines three delivery tiers — **Tier 1 POC-plus** (the main scenario end to end, kept, not thrown away), **Tier 2 Standard**, **Tier 3 Full** — and two tenets: *scope, never rigour* (a tier is small, not sloppy) and *nothing is built ahead* (no part exists because a later tier is expected to need it; a later tier reshaping earlier code is the expected cost). Three things are never deferred: data-loss protection, security on an exposed surface, and visible failure for unhandled cases. Costly-to-reverse decisions are deliberately *not* protected — simplicity wins, and the reversal cost is stated so you can overrule it.
- **Standalone in 3.3.0.** `sdd-flow` did not read the tier standard yet; 3.4.0 added the design-brief gate and tiered delivery to the flow.

### What's new in 3.2.0

Two new user-invoked skills, adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT — see `THIRD-PARTY-NOTICES.md`) and made self-contained, plus one definition of module depth across the plugin.

- **New skill: `improve-codebase-architecture`.** The plugin could review module structure only on paper (the `module-depth` panel specialist reads a spec's `## Modules` section). This skill surveys code that already exists and reports deepening candidates. Upstream's dependencies on its `codebase-design` and `grilling` skills are vendored under `references/`; glossary reads go to `SDD/UBIQUITOUS_LANGUAGE.md` (read-only) and ADRs to `SDD/adr/` via `cross-cutting-adr`. Added over upstream: a `report only` mode, an explicit "no Strong candidates" outcome, a no-network report fallback, and a closing decision summary to paste into `/sdd-flow`.
- **New skill: `retro`.** Looks back at a development cycle and proposes environment changes. Upstream reads one session; a cycle here spans many (`/clear`, compaction, subagents), so this version gathers the record first — session transcripts via the new `scripts/session-digest.py` (stdlib; tests: `python3 -m unittest discover -s scripts/tests` from `skills/retro/`), the `SDD/` records, and git history — and requires every candidate to cite a specific moment. Steering-file advice defers to `improve-claude-md`: navigation fixes go to the code and its neighbouring docs, not to `CLAUDE.md`.
- **One standard for module depth.** `bodies/panel-specialist.md` §4.5, `bodies/planning.md`, `bodies/planning-complete.md`, and the `sdd-spec-module-depth-specialist` agent now define depth as *leverage* — behaviour a caller gets per fact of interface it must learn — and *interface* as everything a caller must know (signatures plus invariants, call order, error modes, configuration, performance bounds). The size comparison between `Public Interface` and `Hides` and the "more than five methods" threshold are gone; the deletion test replaces them. Two anti-patterns are added: **Understated interface** (11) and **Hypothetical seam** (12). Spec field names are unchanged, so existing specs still parse.
- **Reviews find `CODING_STANDARDS.md`.** The project-review-checklist discovery in `bodies/code-review.md` and `bodies/slice-review.md` gains a repo-root `CODING_STANDARDS.md`, after the `CLAUDE.md`/`AGENTS.md` locations and before the PR template — the file `retro` proposes for judgement-call rules when a project has no checklist yet.

### What's new in 3.1.0

- **New skill `rephrase`.** Restates the report you get at the end of a solution, a development phase, or a full cycle as four sections — **Done**, **Pending**, **Blocking**, **Next** — and removes everything else. `/rephrase` with no argument takes the most recent report in the conversation; it also accepts a file path or pasted text, and activates on "rephrase that", "restate that", or "tl;dr".
- **It shortens, it does not improve.** No tests are re-run and no code is re-read. A claim keeps the certainty the original gave it: work that was written but not verified is listed as written, with the verification under Pending. Failures and skipped steps are never dropped for length.
- **Fixed shape.** All four headings appear every time, and an empty one reads `None`, so "nothing is blocking" is distinguishable from a section that was left out. Next steps are numbered, each owned by **You** or **Claude**, and are derived only from what the report already says is unfinished, blocked, or proposed.
- **Not for rewording prose or for handoffs.** "Rephrase this paragraph" stays an ordinary edit, and a handoff to a fresh session still goes through `/adhoc-compact`, which keeps the context this skill removes.

### What's new in 3.0.0

A cleanup release. It is a major version because skills, a command, a spec field, and a flow step are removed.

- **Removed skills: `todo-tidy`, `correction-codifier`, `worktree-create`.** The first two went unused. BB IDE now creates worktrees itself, so `worktree-create` — and the `WORKTREE.md` breadcrumb and `-WT` sibling-directory layout it owned — is gone.
- **`worktree-handoff` is now `worktree-merge`, rewritten.** It no longer assumes a `worktree-create` worktree or a paste-block handoff between two sessions. One session, run from inside the worktree: resolve the target branch (BB's recorded default branch, else the remote's), require committed work, sync with the target *inside the worktree* (rebase when unpublished, merge-in when published), verify, then fast-forward the target — or open a pull request. The main checkout is never left mid-merge. It scans for git-ignored files that would die with the worktree and never copies a provisioned env back into main. Cleanup follows ownership: a BB-managed worktree is left for BB to remove when the thread is archived (with an offer to sweep already-merged branches from earlier threads); any other worktree is removed with its branch, on confirmation.
- **SDD number collisions are settled at merge time, not reserved up front.** `worktree-create` used to reserve ADR/SPEC numbers in `WORKTREE.md`; `sdd-flow`'s research body and `cross-cutting-adr` no longer look for that file. Two worktrees can pick the same number, and `worktree-merge` (Step 3b) detects the duplicate and renumbers this branch's side on confirmation.
- **Eval capture removed (LangSmith).** The `/regression-eval-capture` command, `sdd-flow` Step 4g, and `bodies/eval-capture.md` are gone, as is the `eval_required:` spec frontmatter field (ignored if an older spec still carries it). Steps 4h–4j keep their labels. The `langsmith` CLI is no longer a dependency.
- **`agent_security:` now gates two hook points, not three** — the Step 3c panel value and the Step 4b agentic-surface lens. Abuse cases are still listed by the panel specialist and checked by the review, but they are no longer seeded into an eval dataset.
- **An uncovered abuse case blocks.** In `bodies/code-review.md` and `bodies/slice-review.md`, every relevant abuse case from the catalog's §5 with no test is a HIGH finding, which rejects the implementation or the slice. A test covers a case only if it performs the attack and asserts the expected denial.
- **`bb-worktree-init`** now describes BB IDE as the only caller of the provisioning contract; the `.env-setup.sh` + `.bb-env-setup.sh` symlink layout is unchanged.

### What's new in 2.7.1

- **No more references to a `slice-commit` body that never existed.** The slice bodies described a fourth "slice-commit" primitive; the per-slice commit is the orchestrator's step 4c.6 (conventions in `commands/commit.md`), and the bodies now say so. The slice-ID regex coordination notes now list the six places that actually carry the regex. Wording only; the flow's behaviour is unchanged.

### What's new in 2.6.1

- **Per-slice review now sees the slice's changes.** `bodies/slice-review.md` computed the slice's changed files with `git diff <slice-start-commit>..HEAD`, but a slice is committed only after its review, fixes, and retro — so during review that range compared two identical commits and was always empty (and `git diff` never lists new, untracked files anyway). The reviewer now diffs the working tree against the slice's base commit (excluding `SDD/`, with renames split into old and new paths), lists untracked files and reviews them in full, and prefers this git list over the SPEC's module list when they disagree.
- **Each slice records its base commit.** `slice-start` writes a `Base commit:` line into its `In Progress` progress entry. The review reads it from there, so a resumed session never guesses the base from HEAD, which may already contain the slice.

### What's new in 2.5.0

- **New skill `prompt-doctor`.** Reviews a task prompt before you send it, grading it against the ten-component anatomy from Theo's (T3.gg) prompt dissection plus Sean Goedecke's ranked priorities and hard constraints. Each component gets Present / Weak / Missing / N-A with the quoted span that earns the verdict, and every gap is paired with what the model is now free to decide on its own — in the prompt's own subject matter, not in the abstract.
- **It grades against the right bar.** The run shape (autonomous run / scoped task / one-shot transform) is classified first, so a paragraph rewrite isn't docked for missing stakes and hard constraints. An honest N/A is a passing grade. Only the clear ask and the done-condition are never N/A.
- **It never runs the prompt.** The prompt is a specimen, not an instruction — the skill won't open the issue URL or start the audit the prompt describes. The only files it reads are its own component catalog and, if you point at one, the file holding the draft.
- **It never invents your context.** A missing component produces a question for you, capped at five; it never guesses stakes, deadlines, budgets, or a priority ranking. The rewrite is opt-in, uses only your own words plus your answers, and leaves anything unanswered as a visible `<placeholder>`.
- **`/prompt-doctor`** is the manual entry point.

### What's new in 2.4.0

A one-time setup skill for the BB IDE worktree contract that `worktree-create` requires:

- **New skill `bb-worktree-init`.** Makes a new or existing repo ready for BB IDE and `worktree-create` worktrees. It inspects untracked config, env keys (names and value shapes only — never values), lockfiles, and local databases; proposes a plan for approval; and renders bundled templates into `.worktreeinclude`, `.env-setup.sh`, the `.bb-env-setup.sh` symlink, and — only when setup creates resources outside the worktree — `.bb-env-teardown.sh`. In a repo that already has these files it proposes edits instead of replacing them. It does not commit.
- **The symlink is required, not decoration.** BB IDE only runs `.bb-env-setup.sh`, and a missing one is not an error: BB copies `.env`, skips setup, and opens a worktree whose paths still point at main. The skill always creates the link, checks it, and runs its trial through it.
- **The setup template fails safe.** It refuses to run in the main checkout (comparing symlink-resolved paths, so macOS `/var` vs `/private/var` can't slip past), rewrites *every* copied `.env`/`.env.*` rather than a fixed list, verifies each rewritten path without printing values, fails if main has `.env` but the copy never arrived, and emits the marker line `worktree-handoff` uses to skip reconciliation.
- **Validation before commit.** Syntax, leftover placeholders, symlink, a guard test on a truncated copy of the script, a dry-run of the copy list, and — on approval — a throwaway worktree that is removed afterwards.
- **`worktree-create` points to it** when its precondition gate finds either file missing.

### What's new in 2.3.0

A planning-time gate for goals and constraints that can't both hold:

- **Quantitative Ledger in the spec template.** `bodies/planning.md` adds one table of every numeric goal and constraint, with units and a `Bears on` cross-reference; requirement placeholders now demand numbers, and the planning self-check and quality checklist cover it.
- **Feasibility Arithmetic gate in critical review.** `bodies/critical-review.md` does the subtraction no single reviewer does: when required headroom exceeds what the constraints permit, it is a blocking HIGH finding and an automatic HOLD. Specs with no quantities short-circuit; qualitative stand-ins for quantitative criteria are flagged.

### What's new in 2.2.1

Two defects found running a real per-slice flow, plus one missing review step:

- **The re-planning matcher matched too eagerly.** `sdd-flow`'s Step 4c.5 Stage-1 matcher halted the flow on the mere presence of a `## Recommended Re-planning` header — while the retro-body contract explicitly permitted emitting that header with a `None.` body to mean *no re-planning*. A compliant retro could therefore ask for a re-plan of a plan it had just declared fit. The match is now conjunctive: header present **AND** first non-empty body line is not `None.`
- **The section is now required, not optional.** `## Recommended Re-planning` joins `## Recommended SPEC Amendments` as a mandatory retro section with a mandatory bare `None.` body when there is nothing to recommend. An absent section is a malformed retro, not a "no" — previously nothing distinguished "no re-planning" from "the subagent forgot the section".
- **Never trust the subagent's self-report.** A retro subagent stated it had not emitted the re-planning header; it had. Stage 1 now says explicitly that the artifact is the only evidence — the return supplies the path, the file supplies the answer — and the retro body's return contract requires quoting the section bodies re-read from disk rather than from memory of what it meant to write.
- **New: Project Review Checklist Walk.** Both `bodies/slice-review.md` (Step 5.5) and `bodies/code-review.md` (Step 4b) now discover and walk the project's own review checklist — a `CLAUDE.md`/`AGENTS.md` pre-merge section, a PR template, a named docs checklist — with a PASS/FAIL/N-A verdict and evidence per item. Project bookkeeping items (indexes, status tables, registries) apply even when the code didn't touch them, which is exactly the class of obligation a spec-driven review misses.

### What's new in 2.2.0

Phase-specific compaction is reachable again from an interactive session:

- **New commands `/research-compact`, `/planning-compact`, `/implementation-compact`.** `/adhoc-compact` and `/continue` had redirected to these three names since the 1.0.0 fork, but they only ever existed in the `sdd` plugin — with `agent-engineering` installed alone the redirect pointed at nothing, and with both installed it silently reached sdd's frozen 2.2.0 copies.
- **Wrappers, not a second fork.** Each command resolves `skills/sdd-flow/bodies/<phase>-compact.md` (the same body the orchestrator passes on a Safety-Net trip), tells the model to drop the spawned-subagent framing — no orchestrator, no Reads-counter, no ≤100-word return contract — and follow the rest interactively. The templates stay single-source, so manual and orchestrated compactions cannot drift.
- **Prefixed references.** All three names collide with the `sdd` plugin, so `/adhoc-compact` and `/continue` now name them as `/agent-engineering:<phase>-compact`.
- **`/implementation-compact` confirms before committing.** The body's commit step is correct for a subagent but not for an interactive run; the wrapper requires showing the user what will be staged first.

### What's new in 2.1.0

OWASP AI Agent Security review, as one catalog with two entry points:

- **New skill `ai-agent-security-review`** — standalone, target-detecting (explicit path → active SDD artifact → working diff → repo), writes `SDD/reviews/AGENT-SECURITY-*.md` with the same severity rubric and verdict thresholds as the sdd-flow panel.
- **Vendored control catalog** — `skills/ai-agent-security-review/references/owasp-ai-agent-controls.md`, split into spec-level checks (§3), code-level checks (§4), and the abuse-case test matrix (§5). Deliberately not fetched at review time: reviews must be deterministic and offline-safe. Refresh by re-reading the source and bumping the retrieval date.
- **`sdd-flow` hook points** — `agent-security` panel value (Step 3c, new `sdd-spec-agent-security-specialist` agent, Sonnet); Agentic-Surface Lens in `code-review.md` and `slice-review.md` (Step 4b — a HIGH finding is a rejection criterion); abuse-case seeding in `eval-capture.md` (Step 4g, including an abuse-case-only mode when `eval_required: false`).
- **New spec frontmatter field `agent_security:`** — `auto` (default) | `true` | `false`. The planning body resolves `auto` by agentic-surface detection and appends `agent-security` to `review_panel:`.
- **New orchestrator constant `CATALOG`** — resolved at Step 0 alongside `SKILL_ROOT`. A missing catalog closes the gate for the run with a warning; the flow does not halt.

### What's new in 1.0.3

Hardening from the first live test of the 1.0.2 rotation procedure (three real-fixture runs; findings in `proposals/rotation-test-findings-2026-06-12.md`) plus annotations for the Claude Code 2.1.172 nested-subagents platform change:

- **Byte-fidelity invariant (F1).** Everything that remains in the live `progress.md` after a rotation is preserved byte-identical — never retyped, reflowed, re-encoded, or summarized; the only newly written text is the `## Current State` head and the rotation stamp. (The live test caught a rotation silently mutating 55 kept lines, including meaning changes.)
- **Sub-feature archival granularity (F2).** Size rotation now also archives completed-phase history of the still-active feature (phases with a recorded COMPLETE banner); blocks of the active phase always stay live. Previously a single long-running feature could keep the live file over the ~500-line target indefinitely.
- **Open halt-header matching (F3).** Pending halt blocks are matched by prefix (`## Awaiting *`, `## PARTIAL*`), not a fixed five-entry list — real files contain custom halt headers.
- **Literal phase markers (F4).** The rewritten `## Current State` must carry canonical phase-state lines verbatim (e.g., `Implementation Phase - COMPLETE`) — Phase Detection matches these literal markers, not paraphrases.
- **Nested-subagents annotations.** Claude Code 2.1.172 (2026-06-09) allows nested subagent spawning to depth 5; the flow's one-level rule is now documented everywhere as a deliberate design contract rather than a platform fact, and shipped agents are instructed not to spawn even where the tool works. Analysis, empirical results (including a `general-purpose` spawn-delivery failure on 2.1.174 — prefer named subagent types), and refactor gate criteria: `proposals/nested-subagents-analysis-2026-06-12.md`. The flat architecture is unchanged.

### What's new in 1.0.2

- **Progress hygiene.** `progress.md` no longer grows unboundedly (it sits in the read path of nearly every spawn): feature-completion rotation archives a finished feature's history to `SDD/orchestration/progress-archive/`, leaving a one-line summary; a ~500-line size checkpoint fires at phase-boundary commits; pending halt blocks always carry forward verbatim (phase detection never scans archives). Subagent progress entries are bounded to ≤10 lines — narrative belongs in artifacts. The interactive `/adhoc-compact` and `/continue` commands apply the same rotation in manual sessions.

### What's new in 1.0.1

Post-review fixes to 1.0.0 (no behavioral redesign):

- **Per-slice tracker scaffolding.** New per-slice step 4a.0: the orchestrator spawns `bodies/implementation.md` in scaffold-only mode to create the IMPLEMENTATION-PLAN with its `## Slice Progress` table before the first slice (previously nothing created it, and `slice-start` would halt per FAIL-007). The body's per-slice branch is now explicitly scaffold-only — it never implements slices inline.
- **Interactive `research-clarify` model check stripped** (was carried over from the source verbatim).
- **Consistency fixes:** compaction files and the continuation body now agree on `## Continuation Priorities`; the default panel is enumerated (`security`, `performance`, `data-modeling`, `api-contract`, `module-depth`, + `slice-integrity` in per-slice mode); the tracker template regains its `## Context Management → Essential Files Loaded` section for handoffs; panel specialists return bounded severity counts; residual context-percentage fields replaced with Safety-Net wording; assorted stale labels and cross-references cleaned up.

### What's new in 1.0.0

- **Self-contained fork.** `sdd-flow` no longer depends on the SDD plugin; it ships its own phase bodies, agents, and hook. The SDD plugin is optional and uninstallable.
- **Progressive disclosure.** Slim `SKILL.md` orchestrator core; per-phase chapters under `phases/`; complete subagent instruction sets under `bodies/`.
- **Read-by-path spawning.** Bodies are passed by absolute path, never embedded — there is nothing to strip at runtime.
- **Two-stage specialist panel.** Parallel specialists write `PANEL-FINDINGS-*` files; a synthesis subagent reads them from disk and renders the verdict.
- **Reads-only safety net.** The nested-subagent counter is gone (subagents can't spawn); Reads is the whole signal (>15 default, >20 for implementation chunks).
- **Per-slice authoring default.** Planning favors `delivery_mode: per-slice`; whole-feature requires an explicit one-line justification.
- **Sonnet/Opus routing via shipped agents.** Routing lives in agent frontmatter; the orchestrator may escalate a single spawn via a per-spawn model override.
- **New interactive commands** forked in: `/research-clarify`, `/critical-review`, `/continue`, `/adhoc-compact`, `/commit`.

### History

- **0.4.0–0.6.0** — `sdd-flow` Step 4 became mode-aware (`delivery_mode: whole-feature` | `per-slice`), with the per-slice state machine, slice-boundary checkpoints, rolling learnings ledger, and re-planning. At the time this still depended on the SDD plugin (≥ 2.0.0) for embedded command bodies and shipped agents — a coupling 1.0.0 removes.
- **0.3.0 and earlier** — Initial releases of `correction-codifier`, `cross-cutting-adr`, `improve-claude-md`, `sdd-flow` (whole-feature only), and the `/regression-eval-capture` and `/adr-capture` commands.
